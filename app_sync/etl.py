import hashlib
from django.db import transaction
from typing import Type
from django.db.models import Model
from .connectors import get_mssql_connection

CHUNK_SIZE = 30000 # Increased chunk size since COPY is extremely fast

def get_field_map(model: Type[Model]):
    return {f.name: f.name for f in model._meta.fields if not f.name.startswith('_sync_')}

def compute_row_checksum(row: dict, key_fields: list) -> str:
    values = '|'.join(str(row.get(f, '')) for f in key_fields)
    return hashlib.md5(values.encode()).hexdigest()

import csv
import io
import datetime
from django.db import connection

def _upsert_batch_csv(model, rows, columns, field_map, pk_field, server, new_checksums=None):
    if not rows: return
    
    db_cols = [col for col in columns if col in field_map]
    csv_cols = db_cols + ['_sync_server_id', '_sync_checksum', '_sync_created', '_sync_updated']
    
    # Deduplicate rows by pk_field to prevent "ON CONFLICT DO UPDATE command cannot affect row a second time"
    # Keeping the last occurrence in the batch.
    pk_idx = columns.index(pk_field)
    unique_rows_map = {}
    unique_checksums_map = {}
    
    for i, row in enumerate(rows):
        pk_val = row[pk_idx]
        unique_rows_map[pk_val] = row
        if new_checksums:
            unique_checksums_map[pk_val] = new_checksums[i]
            
    deduped_rows = list(unique_rows_map.values())
    
    buffer = io.StringIO()
    writer = csv.writer(buffer, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    writer.writerow(csv_cols)
    
    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    for i, row in enumerate(deduped_rows):
        row_dict = dict(zip(columns, row))
        out_row = []
        for col in db_cols:
            val = row_dict[col]
            if val is None:
                out_row.append(r'\N')
            elif isinstance(val, (datetime.datetime, datetime.date)):
                out_row.append(val.strftime('%Y-%m-%d %H:%M:%S'))
            elif isinstance(val, bool):
                out_row.append('t' if val else 'f')
            elif isinstance(val, bytes):
                out_row.append('') # Skip binary (foto) for now
            elif isinstance(val, str):
                out_row.append(val.replace('\x00', ''))
            else:
                out_row.append(str(val))
                
        out_row.append(str(server.pk))
        if new_checksums:
            pk_val = row[pk_idx]
            out_row.append(unique_checksums_map[pk_val])
        else:
            out_row.append('')
        out_row.append(now)
        out_row.append(now)
        
        writer.writerow(out_row)
        
    buffer.seek(0)
    
    table_name = model._meta.db_table
    temp_table = f"{table_name}_temp"
    
    with connection.cursor() as cursor:
        cursor.execute(f'CREATE TEMP TABLE IF NOT EXISTS "{temp_table}" (LIKE "{table_name}" INCLUDING DEFAULTS)')
        cursor.execute(f'ALTER TABLE "{temp_table}" DROP COLUMN IF EXISTS "id"')
        cursor.execute(f'TRUNCATE "{temp_table}"')
        
        quoted_csv_cols = [f'"{c}"' for c in csv_cols]
        cols_str = ','.join(quoted_csv_cols)
        
        copy_sql = f'COPY "{temp_table}" ({cols_str}) FROM STDIN WITH (FORMAT CSV, HEADER TRUE, NULL \'\\N\')'
        cursor.copy_expert(copy_sql, buffer)
        
        update_cols = [col for col in csv_cols if col != pk_field]
        set_clause = ', '.join([f'"{col}" = EXCLUDED."{col}"' for col in update_cols])
        
        upsert_query = f"""
            INSERT INTO "{table_name}" ({cols_str})
            SELECT {cols_str} FROM "{temp_table}"
            ON CONFLICT ("{pk_field}") 
            DO UPDATE SET {set_clause}
        """
        cursor.execute(upsert_query)
        cursor.execute(f'DROP TABLE "{temp_table}"')

def _insert_details_batch_csv(model, rows, columns, field_map, fk_field, chunk_pks, server):
    if not rows: return
    
    db_cols = [col for col in columns if col in field_map]
    csv_cols = db_cols + ['_sync_server_id', '_sync_checksum', '_sync_created', '_sync_updated']
    
    buffer = io.StringIO()
    writer = csv.writer(buffer, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    writer.writerow(csv_cols)
    
    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    for row in rows:
        row_dict = dict(zip(columns, row))
        out_row = []
        for col in db_cols:
            val = row_dict[col]
            if val is None:
                out_row.append(r'\N')
            elif isinstance(val, (datetime.datetime, datetime.date)):
                out_row.append(val.strftime('%Y-%m-%d %H:%M:%S'))
            elif isinstance(val, bool):
                out_row.append('t' if val else 'f')
            elif isinstance(val, bytes):
                out_row.append('')
            elif isinstance(val, str):
                out_row.append(val.replace('\x00', ''))
            else:
                out_row.append(str(val))
                
        out_row.append(str(server.pk))
        out_row.append('')
        out_row.append(now)
        out_row.append(now)
        
        writer.writerow(out_row)
        
    buffer.seek(0)
    table_name = model._meta.db_table
    temp_table = f"{table_name}_temp"
    
    with connection.cursor() as cursor:
        cursor.execute(f'CREATE TEMP TABLE IF NOT EXISTS "{temp_table}" (LIKE "{table_name}" INCLUDING DEFAULTS)')
        cursor.execute(f'ALTER TABLE "{temp_table}" DROP COLUMN IF EXISTS "id"')
        cursor.execute(f'TRUNCATE "{temp_table}"')
        
        quoted_csv_cols = [f'"{c}"' for c in csv_cols]
        cols_str = ','.join(quoted_csv_cols)
        
        copy_sql = f'COPY "{temp_table}" ({cols_str}) FROM STDIN WITH (FORMAT CSV, HEADER TRUE, NULL \'\\N\')'
        cursor.copy_expert(copy_sql, buffer)
        
        format_strings = ','.join(['%s'] * len(chunk_pks))
        cursor.execute(f'DELETE FROM "{table_name}" WHERE "{fk_field}" IN ({format_strings}) AND "_sync_server_id" = %s', tuple(chunk_pks) + (server.pk,))
        
        insert_query = f'INSERT INTO "{table_name}" ({cols_str}) SELECT {cols_str} FROM "{temp_table}"'
        cursor.execute(insert_query)
        cursor.execute(f'DROP TABLE "{temp_table}"')

def _sync_details_for_headers_csv(cursor_odbc, detail_table, detail_model, fk_field, header_pks, server):
    if not header_pks:
        return
        
    d_field_map = get_field_map(detail_model)
    chunk_size = 1000
    
    for i in range(0, len(header_pks), chunk_size):
        chunk_pks = header_pks[i:i+chunk_size]
        placeholders = ','.join(['?'] * len(chunk_pks))
        cursor_odbc.execute(f"SELECT * FROM {detail_table} WHERE {fk_field} IN ({placeholders})", chunk_pks)
        d_rows = cursor_odbc.fetchall()
        if d_rows:
            d_columns = [col[0] for col in cursor_odbc.description]
            _insert_details_batch_csv(detail_model, d_rows, d_columns, d_field_map, fk_field, chunk_pks, server)

def sync_incremental(server, table_name: str, model: Type[Model], pk_field: str, start_date=None, end_date=None, date_field='tanggal_server', detail_syncs=None, progress_callback=None):
    from app_core.models import SyncLog
    last_log = SyncLog.objects.filter(
        server=server, tabel=table_name, status='success'
    ).order_by('-selesai_pada').first()

    last_sync = last_log.selesai_pada if last_log else '2000-01-01'
    field_map = get_field_map(model)

    with get_mssql_connection(server) as conn:
        cursor = conn.cursor()
        
        if start_date and end_date:
            cursor.execute(f"SELECT COUNT(*) FROM {table_name} WHERE {date_field} BETWEEN ? AND ?", [start_date, end_date])
        else:
            cursor.execute(f"SELECT COUNT(*) FROM {table_name} WHERE {date_field} > ?", [last_sync])
            
        total = cursor.fetchone()[0]

        offset = 0
        processed = 0
        while True:
            if start_date and end_date:
                cursor.execute(
                    f"""SELECT * FROM {table_name}
                        WHERE {date_field} BETWEEN ? AND ?
                        ORDER BY {date_field}
                        OFFSET ? ROWS FETCH NEXT ? ROWS ONLY""",
                    [start_date, end_date, offset, CHUNK_SIZE]
                )
            else:
                cursor.execute(
                    f"""SELECT * FROM {table_name}
                        WHERE {date_field} > ?
                        ORDER BY {date_field}
                        OFFSET ? ROWS FETCH NEXT ? ROWS ONLY""",
                    [last_sync, offset, CHUNK_SIZE]
                )
            rows = cursor.fetchall()
            if not rows:
                break

            columns = [col[0] for col in cursor.description]
            _upsert_batch_csv(model, rows, columns, field_map, pk_field, server)

            # Sync details for this batch of headers
            if detail_syncs and rows:
                pk_index = columns.index(pk_field)
                header_pks = [row[pk_index] for row in rows]
                for d_model, d_fk in detail_syncs:
                    _sync_details_for_headers_csv(cursor, d_model._meta.db_table, d_model, d_fk, header_pks, server)

            processed += len(rows)
            offset += CHUNK_SIZE
            if progress_callback:
                progress_callback(processed, total)

def sync_checksum_compare(server, table_name, model, pk_field, skip_fields_if_exists=None, progress_callback=None):
    field_map = get_field_map(model)
    with get_mssql_connection(server) as conn:
        cursor = conn.cursor()
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        total = cursor.fetchone()[0]

        offset = 0
        processed = 0
        while True:
            cursor.execute(
                f"""SELECT * FROM {table_name}
                    ORDER BY {pk_field}
                    OFFSET ? ROWS FETCH NEXT ? ROWS ONLY""",
                [offset, CHUNK_SIZE]
            )
            rows = cursor.fetchall()
            if not rows:
                break

            columns = [col[0] for col in cursor.description]
            
            # Compute checksums for the batch
            new_checksums = []
            for row in rows:
                d = dict(zip(columns, row))
                new_checksums.append(compute_row_checksum(d, list(field_map.keys())))
                
            _upsert_batch_csv(model, rows, columns, field_map, pk_field, server, new_checksums=new_checksums)
            
            processed += len(rows)
            offset += CHUNK_SIZE
            if progress_callback:
                progress_callback(processed, total)

def sync_with_gudang_rule(table_name: str, model: Type[Model], pk_field: str, all_servers: list):
    gudang_servers = [s for s in all_servers if s.tipe == 'gudang']
    for server in gudang_servers:
        sync_checksum_compare(server, table_name, model, pk_field)

    other_servers = [s for s in all_servers if s.tipe != 'gudang']
    for server in other_servers:
        sync_checksum_compare(
            server, table_name, model, pk_field,
            skip_fields_if_exists=['nama', 'status']
        )
