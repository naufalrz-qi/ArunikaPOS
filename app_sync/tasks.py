from django.utils import timezone
from app_core.models import SyncLog, ServerConfig
from app_master.models import Kategori, Satuan, Merk, Barang, Customer
import app_transaksi.models as trx_models
from app_sync.etl import sync_incremental, sync_checksum_compare
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

sync_lock = threading.Lock()

from django.conf import settings
import os


TRANSAKSI_SYNC_ORDER = [
    (trx_models.Absensi, 'id', 'tanggal_server', []),
    (trx_models.AbsensiPegawaiLain, 'no_transaksi', 'tanggal', []),
    (trx_models.BiayaOperasional, 'no_transaksi', 'tanggal', []),
    (trx_models.Gaji, 'no_bayar', 'tanggal', []),
    (trx_models.HutangAsetCicilan, 'no_cicilan', 'tanggal', []),
    (trx_models.HutangBiayaAngkutCicilan, 'no_cicilan', 'tanggal', []),
    (trx_models.HutangCicilan, 'no_cicilan', 'tanggal', []),
    (trx_models.HutangPegawai, 'no_transaksi', 'tanggal', []),
    (trx_models.HutangPegawaiCicilan, 'no_cicilan', 'tanggal', []),
    (trx_models.KendaraanJarakTempuh, 'kd_jarak_tempuh', 'tanggal', []),
    (trx_models.KendaraanPengisianBbm, 'kd_pengisian_bbm', 'tanggal', []),
    (trx_models.KendaraanPerawatan, 'no_STNK', 'tanggal', []),
    (trx_models.KendaraanTanggungJawab, 'no_STNK', 'tanggal', []),
    (trx_models.MutasiKas, 'no_transaksi', 'tanggal', []),
    (trx_models.MutasiStok, 'no_transaksi', 'tanggal', [(trx_models.MutasiStokDetail, 'no_transaksi')]),
    (trx_models.OpnameProses, 'no_transaksi', 'tanggal', []),
    (trx_models.OpnameStok, 'no_transaksi', 'tanggal', []),
    (trx_models.PegawaiGantiShift, 'no_transaksi', 'tanggal', [(trx_models.PegawaiGantiShiftDetail, 'no_transaksi')]),
    (trx_models.PegawaiIzin, 'no_transaksi', 'tanggal', []),
    (trx_models.PegawaiLembur, 'no_transaksi', 'tanggal_server', [(trx_models.PegawaiLemburDetail, 'no_transaksi')]),
    (trx_models.PegawaiSuratPeringatan, 'no_sp', 'tanggal', []),
    (trx_models.PemakaianBarang, 'no_transaksi', 'tanggal', [(trx_models.PemakaianBarangDetail, 'no_transaksi')]),
    (trx_models.Pembelian, 'no_transaksi', 'tanggal', [(trx_models.PembelianDetail, 'no_transaksi')]),
    (trx_models.PembelianOrder, 'no_order', 'tanggal', [(trx_models.PembelianOrderDetail, 'no_order')]),
    (trx_models.PembelianOrderSparePart, 'no_order', 'tanggal', [(trx_models.PembelianOrderSparePartDetail, 'no_order')]),
    (trx_models.PembelianRetur, 'no_retur', 'tanggal', [(trx_models.PembelianReturDetail, 'no_retur')]),
    (trx_models.PenambahanKas, 'no_transaksi', 'tanggal', []),
    (trx_models.Pendapatan, 'no_transaksi', 'tanggal', []),
    (trx_models.Penjualan, 'no_transaksi', 'tanggal', [(trx_models.PenjualanDetail, 'no_transaksi'), (trx_models.PenjualanDetailPegawai, 'no_transaksi')]),
    (trx_models.PenjualanJasa, 'no_transaksi', 'tanggal_server', [(trx_models.PenjualanJasaDetail, 'no_transaksi')]),
    (trx_models.PenjualanNotaKosong, 'no_transaksi', 'tanggal_server', []),
    (trx_models.PenjualanOrder, 'no_order', 'tanggal', [(trx_models.PenjualanOrderDetail, 'no_order')]),
    (trx_models.PenjualanPoint, 'no_transaksi', 'tanggal', []),
    (trx_models.PenjualanRetur, 'no_retur', 'tanggal', [(trx_models.PenjualanReturDetail, 'no_retur')]),
    (trx_models.PenjualanSelected, 'no_transaksi', 'tanggal', []),
    (trx_models.PiutangCicilan, 'no_cicilan', 'tanggal', []),
    (trx_models.PiutangJasaCicilan, 'no_cicilan', 'tanggal', []),
    (trx_models.Prive, 'no_transaksi', 'tanggal', []),
    (trx_models.Sewa, 'no_transaksi', 'tanggal', []),
]



def _update_progress(log: SyncLog, current: int, total: int, tbl_name: str = ''):
    """Update progress di DB untuk polling frontend."""
    with sync_lock:
        log.refresh_from_db()
        if log.status == 'cancelled':
            raise ValueError("Dibatalkan oleh pengguna")
            
        details = log.details or {}
        
        if tbl_name not in details:
            details[tbl_name] = {'current': 0, 'total': 0, 'status': 'syncing'}
            
        details[tbl_name]['current'] = current
        details[tbl_name]['total'] = total
        # If total is > 0 and current == total, mark done. Else syncing. 
        # If total is 0, we can also consider it done.
        if total > 0 and current >= total:
            details[tbl_name]['status'] = 'done'
        elif total == 0:
            details[tbl_name]['status'] = 'done'
        else:
            details[tbl_name]['status'] = 'syncing'
        
        # Calculate overall
        total_data_all = sum(d.get('total', 0) for d in details.values())
        current_data_all = sum(d.get('current', 0) for d in details.values())
        pct = round((current_data_all / total_data_all * 100) if total_data_all > 0 else 0, 1)

        log.details = details
        log.progress_pct = pct
        log.data_baru = current_data_all
        log.total_data = total_data_all
        log.save(update_fields=['details', 'progress_pct', 'data_baru', 'total_data'])

def task_full_sync(log_id: int, server_id: int):
    """Full Sync: Tarik semua data dari satu server MSSQL."""
    server = ServerConfig.objects.get(pk=server_id)
    log = SyncLog.objects.get(pk=log_id)
    
    try:
        import app_master.models as master_models
        from django.db import models
        
        SYNC_ORDER = []
        for name in dir(master_models):
            obj = getattr(master_models, name)
            if isinstance(obj, type) and issubclass(obj, models.Model) and obj.__module__ == 'app_master.models':
                if hasattr(obj, '_meta') and not obj._meta.abstract:
                    table_name = obj._meta.db_table
                    if table_name.startswith('m_'):
                        pk_field = obj._meta.pk.name
                        SYNC_ORDER.append((table_name, obj, pk_field))
        
        # Initialize details
        if not log.details:
            log.details = {tbl: {'current': 0, 'total': 0, 'status': 'pending'} for tbl, _, _ in SYNC_ORDER}
            log.save(update_fields=['details'])
            
        for tbl, model, pk in SYNC_ORDER:
            sync_checksum_compare(
                server, tbl, model, pk, 
                progress_callback=lambda c, t, tbl_name=tbl: _update_progress(log, c, t, tbl_name)
            )

        # Mark all as done
        log.refresh_from_db()
        for tbl in log.details:
            log.details[tbl]['status'] = 'done'
            
        log.status = 'success'
        log.selesai_pada = timezone.now()
        log.save()
        return "Full sync completed successfully."
    except Exception as e:
        log.refresh_from_db()
        if log.status != 'cancelled':
            log.status = 'failed'
            log.pesan_error = str(e)
            log.selesai_pada = timezone.now()
            log.save(update_fields=['status', 'pesan_error', 'selesai_pada'])
        raise

def task_auto_sync(log_id: int, server_id: int, start_date=None, end_date=None):
    """Manual Sync Transaksi: Berdasarkan rentang waktu."""
    server = ServerConfig.objects.get(pk=server_id)
    log = SyncLog.objects.get(pk=log_id)
    try:
        # Initialize details
        if not log.details:
            log.details = {model._meta.db_table: {'current': 0, 'total': 0, 'status': 'pending'} for model, _, _, _ in TRANSAKSI_SYNC_ORDER}
            log.save(update_fields=['details'])
            
        for model, pk, date_field, details in TRANSAKSI_SYNC_ORDER:
            tbl = model._meta.db_table
            sync_incremental(
                server, tbl, model, pk,
                start_date, end_date, date_field, details,
                lambda c, t, tbl_name=tbl: _update_progress(log, c, t, tbl_name)
            )
        
        # Mark all as done
        log.refresh_from_db()
        for tbl in log.details:
            log.details[tbl]['status'] = 'done'
            
        log.status = 'success'
        log.selesai_pada = timezone.now()
        log.save()
        return "Manual sync transaksi completed successfully."
    except Exception as e:
        log.refresh_from_db()
        if log.status != 'cancelled':
            log.status = 'failed'
            log.pesan_error = str(e)
            log.selesai_pada = timezone.now()
            log.save(update_fields=['status', 'pesan_error', 'selesai_pada'])
        raise

def task_sequential_auto_sync():
    """Auto Sync (Realtime): Hanya tabel transaksi 3 hari terakhir berantai."""
    import datetime
    servers = ServerConfig.objects.filter(is_active=True)
    if not servers.exists():
        return "No active servers."
    
    end_date = timezone.now()
    start_date = end_date - datetime.timedelta(days=3)
    
    for server in servers:
        log = SyncLog.objects.create(
            server=server, 
            jenis='auto_sync_3d', 
            status='running'
        )
        
        try:
            # Initialize details
            log.details = {model._meta.db_table: {'current': 0, 'total': 0, 'status': 'pending'} for model, _, _, _ in TRANSAKSI_SYNC_ORDER}
            log.save(update_fields=['details'])
            
            for model, pk, date_field, details in TRANSAKSI_SYNC_ORDER:
                tbl = model._meta.db_table
                sync_incremental(
                    server, tbl, model, pk,
                    start_date.strftime('%Y-%m-%d %H:%M:%S'), 
                    end_date.strftime('%Y-%m-%d %H:%M:%S'), 
                    date_field, details,
                    lambda c, t, tbl_name=tbl: _update_progress(log, c, t, tbl_name)
                )
            
            log.refresh_from_db()
            for tbl in log.details:
                log.details[tbl]['status'] = 'done'
                
            log.status = 'success'
            log.selesai_pada = timezone.now()
            log.save()
            
        except Exception as e:
            log.refresh_from_db()
            if log.status != 'cancelled':
                log.status = 'failed'
                log.pesan_error = str(e)
                log.selesai_pada = timezone.now()
                log.save(update_fields=['status', 'pesan_error', 'selesai_pada'])

def task_monthly_check(server_id: int):
    return "Monthly check skipped for MVP"

def task_yearly_check(server_id: int):
    return "Yearly check skipped for MVP"

def task_full_check(server_id: int):
    return "Full check skipped for MVP"

def task_price_sync(server_id: int, barang_list: list):
    return "Price sync skipped for MVP"
