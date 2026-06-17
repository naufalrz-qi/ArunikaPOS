import os

def parse_txt(filepath):
    tables = {}
    with open(filepath, 'r') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            parts = line.split('\t')
            if len(parts) >= 6:
                table_name = parts[0]
                col_name = parts[1]
                data_type = parts[2]
                length = parts[3]
                is_null = parts[4] == '1'
                is_pk = parts[5] == '1'
                
                if table_name not in tables:
                    tables[table_name] = []
                tables[table_name].append({
                    'col': col_name,
                    'type': data_type,
                    'len': length,
                    'null': is_null,
                    'pk': is_pk
                })
    return tables

def map_type(col_data):
    dt = col_data['type'].lower()
    length = col_data['len']
    is_null = col_data['null']
    
    kwargs = []
    if is_null:
        kwargs.append("null=True")
        kwargs.append("blank=True")
        
    if dt in ('varchar', 'char', 'jr_kode_master', 'jr_no_transaksi', 'jr_no_bukti', 'jr_status_jenis', 'jr_keterangan', 'jr_kode_barang', 'jr_barcode'):
        kwargs.append(f"max_length={length}")
        return f"models.CharField({', '.join(kwargs)})"
    elif dt in ('datetime', 'smalldatetime'):
        return f"models.DateTimeField({', '.join(kwargs)})"
    elif dt == 'money':
        kwargs.append("max_digits=18")
        kwargs.append("decimal_places=2")
        return f"models.DecimalField({', '.join(kwargs)})"
    elif dt in ('float', 'jr_angka_koma'):
        return f"models.FloatField({', '.join(kwargs)})"
    elif dt in ('tinyint', 'int', 'smallint', 'jr_urutan'):
        return f"models.IntegerField({', '.join(kwargs)})"
    elif dt in ('text', 'ntext'):
        return f"models.TextField({', '.join(kwargs)})"
    elif dt == 'bit':
        kwargs.append("default=False")
        kwargs.append("null=True") # adding null=True to bit just in case
        return f"models.BooleanField({', '.join(kwargs)})"
    elif dt == 'image':
        return f"models.BinaryField({', '.join(kwargs)})"
    else:
        kwargs.append(f"max_length={length}")
        return f"models.CharField({', '.join(kwargs)})"

def generate_model_code(table_name, columns):
    class_name = "".join(x.capitalize() for x in table_name.split('_')[1:])
    code = f"class {class_name}(SyncMetaMixin):\n"
    
    # If table has multiple PKs, Django doesn't support composite PKs natively easily in models.
    # We will just mark the first one as primary_key=True and others as normal fields.
    pk_assigned = False
    
    for c in columns:
        col_name = c['col']
        field_def = map_type(c)
        if c['pk'] and not pk_assigned:
            # insert primary_key=True into the kwargs
            if '(' in field_def and field_def.endswith(')'):
                if field_def.endswith('()'):
                    field_def = field_def.replace("()", "(primary_key=True)")
                else:
                    field_def = field_def.replace("(", "(primary_key=True, ", 1)
            pk_assigned = True
            
        code += f"    {col_name} = {field_def}\n"
    
    if not pk_assigned:
        code += f"    # No explicit PK found in schema, Django will add 'id' automatically or you need to define one.\n"
        
    code += "\n    class Meta:\n"
    code += f"        db_table = '{table_name}'\n\n"
    return code

def main():
    tables = parse_txt('strukturdatabase_GrosirPusat.txt')
    
    master_code = "from django.db import models\nfrom app_core.models import ServerConfig\n\n"
    master_code += '''class SyncMetaMixin(models.Model):
    """Mixin untuk metadata sinkronisasi, ditambahkan ke semua model sync."""
    _sync_server    = models.ForeignKey(ServerConfig,
                                        on_delete=models.SET_NULL, null=True,
                                        db_column='_sync_server_id',
                                        related_name='%(app_label)s_%(class)s_related')
    _sync_created   = models.DateTimeField(auto_now_add=True, db_column='_sync_created')
    _sync_updated   = models.DateTimeField(auto_now=True, db_column='_sync_updated')
    _sync_checksum  = models.CharField(max_length=64, blank=True, db_column='_sync_checksum')

    class Meta:
        abstract = True

'''
    
    transaksi_code = "from django.db import models\nfrom app_core.models import ServerConfig\nfrom app_master.models import SyncMetaMixin\n\n"
    
    for table_name, columns in tables.items():
        if table_name.startswith('m_'):
            master_code += generate_model_code(table_name, columns)
        elif table_name.startswith('t_'):
            transaksi_code += generate_model_code(table_name, columns)
            
    with open('app_master/models.py', 'w') as f:
        f.write(master_code)
        
    with open('app_transaksi/models.py', 'w') as f:
        f.write(transaksi_code)
        
    print("Models generated successfully!")

if __name__ == '__main__':
    main()
