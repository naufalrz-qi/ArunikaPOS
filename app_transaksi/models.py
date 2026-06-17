from django.db import models
from app_core.models import ServerConfig
from app_master.models import SyncMetaMixin

class Absensi(SyncMetaMixin):
    id = models.CharField(primary_key=True, max_length=8)
    kd_pegawai = models.CharField(max_length=6)
    masuk = models.DateTimeField(null=True, blank=True)
    keluar = models.DateTimeField(null=True, blank=True)
    tanggal_server = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 't_absensi'

class AbsensiPegawaiLain(SyncMetaMixin):
    no_transaksi = models.CharField(primary_key=True, max_length=20)
    kd_pegawai = models.CharField(max_length=6)
    tanggal = models.DateTimeField()
    jenis = models.CharField(max_length=1)
    keterangan = models.CharField(max_length=50)
    kd_user = models.CharField(max_length=6)
    tanggal_server = models.DateTimeField()

    class Meta:
        db_table = 't_absensi_pegawai_lain'

class BiayaOperasional(SyncMetaMixin):
    no_transaksi = models.CharField(primary_key=True, max_length=20)
    kd_divisi = models.CharField(max_length=6)
    kd_biaya = models.CharField(max_length=6)
    kd_jenis = models.CharField(max_length=6)
    kd_kas = models.CharField(max_length=6)
    tanggal = models.DateTimeField()
    nominal = models.DecimalField(max_digits=18, decimal_places=2)
    no_bukti = models.CharField(max_length=20)
    keterangan = models.CharField(max_length=50)
    kd_user = models.CharField(max_length=6)
    tanggal_server = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 't_biaya_operasional'

class Gaji(SyncMetaMixin):
    no_bayar = models.CharField(primary_key=True, max_length=24)
    tanggal = models.DateTimeField(null=True, blank=True)
    periode = models.DateTimeField(null=True, blank=True)
    kd_pegawai = models.CharField(null=True, blank=True, max_length=6)
    gaji_pokok = models.DecimalField(null=True, blank=True, max_digits=18, decimal_places=2)
    libur_off_jam = models.FloatField(null=True, blank=True)
    libur_off_rp = models.DecimalField(null=True, blank=True, max_digits=18, decimal_places=2)
    lembur_jam = models.FloatField(null=True, blank=True)
    lembur_rp = models.DecimalField(null=True, blank=True, max_digits=18, decimal_places=2)
    kerajinan = models.DecimalField(null=True, blank=True, max_digits=18, decimal_places=2)
    lain_lain_plus = models.DecimalField(null=True, blank=True, max_digits=18, decimal_places=2)
    pinjaman_lalu = models.DecimalField(null=True, blank=True, max_digits=18, decimal_places=2)
    pinjaman_sekarang = models.DecimalField(null=True, blank=True, max_digits=18, decimal_places=2)
    absen_jam = models.FloatField(null=True, blank=True)
    absen_rp = models.DecimalField(null=True, blank=True, max_digits=18, decimal_places=2)
    jamsostek = models.DecimalField(null=True, blank=True, max_digits=18, decimal_places=2)
    lain_lain_min = models.DecimalField(null=True, blank=True, max_digits=18, decimal_places=2)
    keterangan = models.CharField(null=True, blank=True, max_length=100)

    class Meta:
        db_table = 't_gaji'

class HutangAsetCicilan(SyncMetaMixin):
    no_cicilan = models.CharField(primary_key=True, max_length=20)
    kd_aset = models.CharField(max_length=6)
    kd_jenis = models.CharField(max_length=6)
    kd_kas = models.CharField(max_length=6)
    nominal = models.DecimalField(max_digits=18, decimal_places=2)
    tanggal = models.DateTimeField()
    no_bukti = models.CharField(max_length=20)
    keterangan = models.CharField(max_length=50)
    kd_user = models.CharField(max_length=6)
    tanggal_server = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 't_hutang_aset_cicilan'

class HutangBiayaAngkutCicilan(SyncMetaMixin):
    no_cicilan = models.CharField(primary_key=True, max_length=20)
    no_nota = models.CharField(max_length=20)
    tanggal = models.DateTimeField()
    nominal = models.DecimalField(max_digits=18, decimal_places=2)
    kd_jenis = models.CharField(max_length=6)
    kd_kas = models.CharField(max_length=6)
    no_bukti = models.CharField(max_length=20)
    keterangan = models.CharField(max_length=50)
    kd_user = models.CharField(max_length=6)
    tanggal_server = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 't_hutang_biaya_angkut_cicilan'

class HutangCicilan(SyncMetaMixin):
    no_cicilan = models.CharField(primary_key=True, max_length=20)
    no_transaksi = models.CharField(max_length=20)
    kd_jenis = models.CharField(max_length=6)
    kd_kas = models.CharField(max_length=6)
    nominal = models.DecimalField(max_digits=18, decimal_places=2)
    tanggal = models.DateTimeField()
    no_bukti = models.CharField(max_length=20)
    keterangan = models.CharField(max_length=50)
    kd_user = models.CharField(max_length=6)
    tanggal_server = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 't_hutang_cicilan'

class HutangPegawai(SyncMetaMixin):
    no_transaksi = models.CharField(primary_key=True, max_length=20)
    kd_pegawai = models.CharField(max_length=6)
    tanggal = models.DateTimeField()
    kd_jenis = models.CharField(max_length=6)
    kd_kas = models.CharField(max_length=6)
    no_bukti = models.CharField(max_length=20)
    nominal = models.DecimalField(max_digits=18, decimal_places=2)
    keterangan = models.CharField(max_length=50)
    kd_user = models.CharField(max_length=6)
    tanggal_server = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 't_hutang_pegawai'

class HutangPegawaiCicilan(SyncMetaMixin):
    no_cicilan = models.CharField(primary_key=True, max_length=20)
    no_transaksi = models.CharField(max_length=20)
    kd_jenis = models.CharField(max_length=6)
    kd_kas = models.CharField(max_length=6)
    no_bukti = models.CharField(max_length=20)
    tanggal = models.DateTimeField()
    nominal = models.DecimalField(max_digits=18, decimal_places=2)
    keterangan = models.CharField(max_length=50)
    kd_user = models.CharField(max_length=6)
    tanggal_server = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 't_hutang_pegawai_cicilan'

class KendaraanJarakTempuh(SyncMetaMixin):
    kd_jarak_tempuh = models.CharField(primary_key=True, max_length=8)
    kd_pengisian_bbm = models.CharField(max_length=20)
    tanggal = models.DateTimeField()
    KM = models.CharField(max_length=8)
    keterangan = models.CharField(max_length=50)
    kd_user = models.CharField(max_length=6)
    tanggal_server = models.DateTimeField()

    class Meta:
        db_table = 't_kendaraan_jarak_tempuh'

class KendaraanPengisianBbm(SyncMetaMixin):
    kd_pengisian_bbm = models.CharField(primary_key=True, max_length=20)
    no_STNK = models.CharField(max_length=15)
    tanggal = models.DateTimeField()
    BBM = models.FloatField()
    keterangan = models.CharField(max_length=50)
    kd_user = models.CharField(max_length=6)
    tanggal_server = models.DateTimeField()

    class Meta:
        db_table = 't_kendaraan_pengisian_bbm'

class KendaraanPerawatan(SyncMetaMixin):
    no_STNK = models.CharField(primary_key=True, max_length=15)
    kd_jenis_perawatan = models.CharField(max_length=8)
    tanggal = models.DateTimeField()
    KM = models.CharField(max_length=8)
    keterangan = models.CharField(max_length=50)
    kd_user = models.CharField(max_length=6)
    tanggal_server = models.DateTimeField()

    class Meta:
        db_table = 't_kendaraan_perawatan'

class KendaraanTanggungJawab(SyncMetaMixin):
    no_STNK = models.CharField(primary_key=True, max_length=15)
    kd_pegawai = models.CharField(max_length=6)
    tanggal = models.DateTimeField()
    keterangan = models.CharField(max_length=50)
    kd_user = models.CharField(max_length=6)
    Tanggal_server = models.DateTimeField()

    class Meta:
        db_table = 't_kendaraan_tanggung_jawab'

class MutasiKas(SyncMetaMixin):
    no_transaksi = models.CharField(primary_key=True, max_length=20)
    tanggal = models.DateTimeField()
    kd_kas_sumber = models.CharField(max_length=6)
    kd_kas_tujuan = models.CharField(max_length=10)
    nominal = models.DecimalField(max_digits=18, decimal_places=2)
    no_bukti_sumber = models.CharField(max_length=20)
    no_bukti_tujuan = models.CharField(max_length=20)
    keterangan = models.CharField(max_length=50)
    kd_user = models.CharField(max_length=6)
    tanggal_server = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 't_mutasi_kas'

class MutasiStok(SyncMetaMixin):
    no_transaksi = models.CharField(primary_key=True, max_length=20)
    kd_divisi_asal = models.CharField(max_length=6)
    kd_divisi_tujuan = models.CharField(max_length=6)
    tanggal = models.DateTimeField()
    keterangan = models.CharField(max_length=50)
    kd_user = models.CharField(max_length=6)
    tanggal_server = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 't_mutasi_stok'

class MutasiStokDetail(SyncMetaMixin):
    no_transaksi = models.CharField(primary_key=True, max_length=20)
    kd_barang = models.CharField(max_length=30)
    kd_satuan = models.CharField(max_length=6)
    qty = models.FloatField()

    class Meta:
        db_table = 't_mutasi_stok_detail'

class OpnameProses(SyncMetaMixin):
    no_transaksi = models.CharField(primary_key=True, max_length=8)
    kd_divisi = models.CharField(max_length=10)
    kd_barang = models.CharField(max_length=30)
    kd_satuan = models.CharField(max_length=6)
    tanggal = models.DateTimeField()
    qty = models.FloatField()
    status = models.CharField(max_length=1)
    kd_user = models.CharField(max_length=6)
    tanggal_server = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 't_opname_proses'

class OpnameStok(SyncMetaMixin):
    no_transaksi = models.CharField(primary_key=True, max_length=20)
    kd_divisi = models.CharField(max_length=6)
    kd_barang = models.CharField(max_length=30)
    kd_satuan = models.CharField(max_length=6)
    tanggal = models.DateTimeField()
    qty = models.FloatField()
    keterangan = models.CharField(max_length=50)
    kd_user = models.CharField(max_length=6)
    status = models.CharField(max_length=1)
    tanggal_server = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 't_opname_stok'

class PegawaiGantiShift(SyncMetaMixin):
    no_transaksi = models.CharField(primary_key=True, max_length=8)
    tanggal = models.DateTimeField(null=True, blank=True)
    keterangan = models.CharField(null=True, blank=True, max_length=50)
    kd_user = models.CharField(null=True, blank=True, max_length=6)
    tanggal_server = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 't_pegawai_ganti_shift'

class PegawaiGantiShiftDetail(SyncMetaMixin):
    no_transaksi = models.CharField(primary_key=True, max_length=8)
    kd_pegawai = models.CharField(max_length=6)
    kd_shift = models.CharField(max_length=6)

    class Meta:
        db_table = 't_pegawai_ganti_shift_detail'

class PegawaiIzin(SyncMetaMixin):
    no_transaksi = models.CharField(primary_key=True, max_length=20)
    kd_pegawai = models.CharField(max_length=6)
    kd_izin = models.CharField(max_length=6)
    tanggal = models.DateTimeField()
    awal = models.DateTimeField()
    akhir = models.DateTimeField()
    status = models.CharField(max_length=1)
    keterangan = models.CharField(max_length=50)
    kd_user = models.CharField(max_length=6)
    tanggal_server = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 't_pegawai_izin'

class PegawaiLembur(SyncMetaMixin):
    no_transaksi = models.CharField(primary_key=True, max_length=20)
    kd_divisi = models.CharField(max_length=6)
    awal = models.DateTimeField()
    akhir = models.DateTimeField()
    keterangan = models.CharField(max_length=50)
    kd_user = models.CharField(max_length=6)
    tanggal_server = models.DateTimeField()

    class Meta:
        db_table = 't_pegawai_lembur'

class PegawaiLemburDetail(SyncMetaMixin):
    no_transaksi = models.CharField(primary_key=True, max_length=20)
    kd_pegawai = models.CharField(max_length=6)

    class Meta:
        db_table = 't_pegawai_lembur_detail'

class PegawaiSuratPeringatan(SyncMetaMixin):
    no_sp = models.CharField(primary_key=True, max_length=20)
    kd_pegawai = models.CharField(max_length=6)
    tanggal = models.DateTimeField()
    keterangan = models.CharField(max_length=50)
    status = models.CharField(max_length=1)
    kd_user = models.CharField(max_length=6)
    tanggal_server = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 't_pegawai_surat_peringatan'

class PemakaianBarang(SyncMetaMixin):
    no_transaksi = models.CharField(primary_key=True, max_length=20)
    tanggal = models.DateTimeField()
    keterangan = models.CharField(max_length=50)
    kd_user = models.CharField(max_length=6)
    tanggal_server = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 't_pemakaian_barang'

class PemakaianBarangDetail(SyncMetaMixin):
    no_transaksi = models.CharField(primary_key=True, max_length=20)
    kd_barang = models.CharField(max_length=30)
    kd_satuan = models.CharField(max_length=6)
    qty = models.FloatField(null=True, blank=True)

    class Meta:
        db_table = 't_pemakaian_barang_detail'

class Pembelian(SyncMetaMixin):
    no_transaksi = models.CharField(primary_key=True, max_length=20)
    kd_supplier = models.CharField(max_length=6)
    kd_divisi = models.CharField(max_length=6)
    kd_jenis = models.CharField(max_length=6)
    kd_kas = models.CharField(max_length=6)
    no_order = models.CharField(max_length=50)
    tanggal = models.DateTimeField()
    tanggal_jatuh_tempo = models.DateTimeField()
    status = models.CharField(max_length=1)
    diskon1 = models.FloatField()
    diskon2 = models.FloatField()
    diskon3 = models.FloatField()
    diskon4 = models.FloatField()
    pajak = models.FloatField()
    ppnbm = models.FloatField()
    keterangan = models.CharField(max_length=50)
    kd_user = models.CharField(max_length=6)
    tanggal_server = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 't_pembelian'

class PembelianBiayaAngkut(SyncMetaMixin):
    no_nota = models.CharField(primary_key=True, max_length=20)
    no_transaksi = models.CharField(max_length=20)
    kd_ekspedisi = models.CharField(max_length=6)
    kd_jenis = models.CharField(max_length=6)
    kd_kas = models.CharField(max_length=6)
    nominal = models.DecimalField(max_digits=18, decimal_places=2)
    status = models.CharField(max_length=1)
    tanggal_jatuh_tempo = models.DateTimeField()

    class Meta:
        db_table = 't_pembelian_biaya_angkut'

class PembelianDetail(SyncMetaMixin):
    no_transaksi = models.CharField(max_length=20)
    kd_barang = models.CharField(max_length=30)
    kd_satuan = models.CharField(max_length=6)
    jenis = models.CharField(max_length=1)
    qty = models.FloatField()
    harga_beli = models.DecimalField(max_digits=18, decimal_places=2)
    diskon1 = models.FloatField()
    diskon2 = models.FloatField()
    diskon3 = models.FloatField()
    diskon4 = models.FloatField()
    point1 = models.FloatField()
    total = models.FloatField(null=True, blank=True)
    # No explicit PK found in schema, Django will add 'id' automatically or you need to define one.

    class Meta:
        db_table = 't_pembelian_detail'

class PembelianOrder(SyncMetaMixin):
    no_order = models.CharField(primary_key=True, max_length=50)
    no_pp_order = models.CharField(max_length=20)
    kd_divisi = models.CharField(max_length=6)
    kd_supplier = models.CharField(max_length=6)
    kd_kas = models.CharField(max_length=6)
    kd_jenis_bayar = models.CharField(max_length=6)
    tanggal = models.DateTimeField()
    tanggal_terima = models.DateTimeField()
    status = models.CharField(max_length=1)
    diskon1 = models.FloatField()
    diskon2 = models.FloatField()
    diskon3 = models.FloatField()
    diskon4 = models.FloatField()
    pajak = models.FloatField()
    ppnbm = models.FloatField()
    no_bukti = models.CharField(max_length=20)
    keterangan = models.CharField(max_length=250)
    jaminan = models.DecimalField(max_digits=18, decimal_places=2)
    kd_user = models.CharField(max_length=6)
    tanggal_server = models.DateTimeField()
    no_transaksi = models.CharField(max_length=20)

    class Meta:
        db_table = 't_pembelian_order'

class PembelianOrderDetail(SyncMetaMixin):
    no_order = models.CharField(max_length=50)
    kd_barang = models.CharField(primary_key=True, max_length=30)
    kd_satuan = models.CharField(max_length=6)
    jenis = models.CharField(max_length=1)
    qty = models.FloatField()
    harga_beli = models.DecimalField(max_digits=18, decimal_places=2)
    diskon1 = models.FloatField()
    diskon2 = models.FloatField()
    diskon3 = models.FloatField()
    diskon4 = models.FloatField()

    class Meta:
        db_table = 't_pembelian_order_detail'

class PembelianOrderSparePart(SyncMetaMixin):
    no_order = models.CharField(primary_key=True, max_length=20)
    kd_divisi = models.CharField(max_length=6)
    no_pp_order = models.CharField(max_length=20)
    kd_supplier = models.CharField(max_length=6)
    tanggal = models.DateTimeField()
    tanggal_terima = models.DateTimeField()
    status = models.CharField(max_length=1)
    keterangan = models.CharField(max_length=250)
    diskon = models.FloatField()
    pajak = models.FloatField()
    ppnbm = models.FloatField()
    kd_user = models.CharField(max_length=6)
    tanggal_server = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 't_pembelian_order_spare_part'

class PembelianOrderSparePartDetail(SyncMetaMixin):
    no_order = models.CharField(max_length=20)
    barang = models.CharField(max_length=50)
    qty = models.FloatField()
    satuan = models.CharField(null=True, blank=True, max_length=35)
    harga_beli = models.DecimalField(max_digits=18, decimal_places=2)
    diskon = models.FloatField()
    # No explicit PK found in schema, Django will add 'id' automatically or you need to define one.

    class Meta:
        db_table = 't_pembelian_order_spare_part_detail'

class PembelianRetur(SyncMetaMixin):
    no_retur = models.CharField(primary_key=True, max_length=20)
    kd_divisi = models.CharField(max_length=6)
    kd_supplier = models.CharField(max_length=6)
    kd_jenis = models.CharField(max_length=6)
    kd_kas = models.CharField(max_length=6)
    tanggal = models.DateTimeField()
    no_bukti = models.CharField(max_length=20)
    diskon1 = models.FloatField()
    diskon2 = models.FloatField()
    diskon3 = models.FloatField()
    diskon4 = models.FloatField()
    pajak = models.FloatField()
    ppnbm = models.FloatField()
    keterangan = models.CharField(max_length=50)
    kd_user = models.CharField(max_length=6)
    tanggal_server = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 't_pembelian_retur'

class PembelianReturDetail(SyncMetaMixin):
    no_retur = models.CharField(primary_key=True, max_length=20)
    kd_barang = models.CharField(max_length=30)
    kd_satuan = models.CharField(max_length=6)
    qty = models.FloatField()
    harga = models.DecimalField(max_digits=18, decimal_places=2)
    diskon1 = models.FloatField()
    diskon2 = models.FloatField()
    diskon3 = models.FloatField()
    diskon4 = models.FloatField()

    class Meta:
        db_table = 't_pembelian_retur_detail'

class PenambahanKas(SyncMetaMixin):
    no_transaksi = models.CharField(primary_key=True, max_length=20)
    tanggal = models.DateTimeField()
    kd_kas = models.CharField(max_length=6)
    nominal = models.DecimalField(max_digits=18, decimal_places=2)
    keterangan = models.CharField(max_length=50)
    kd_user = models.CharField(max_length=6)

    class Meta:
        db_table = 't_penambahan_kas'

class Pendapatan(SyncMetaMixin):
    no_transaksi = models.CharField(primary_key=True, max_length=20)
    kd_divisi = models.CharField(max_length=6)
    kd_pendapatan = models.CharField(max_length=6)
    kd_jenis = models.CharField(max_length=6)
    kd_kas = models.CharField(max_length=6)
    tanggal = models.DateTimeField()
    nominal = models.DecimalField(max_digits=18, decimal_places=2)
    no_bukti = models.CharField(max_length=20)
    keterangan = models.CharField(max_length=50)
    kd_user = models.CharField(max_length=6)
    tanggal_server = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 't_pendapatan'

class Penjualan(SyncMetaMixin):
    no_transaksi = models.CharField(primary_key=True, max_length=20)
    kd_customer = models.CharField(max_length=20)
    kd_divisi = models.CharField(max_length=6)
    kd_jenis = models.CharField(max_length=6)
    kd_kas = models.CharField(max_length=6)
    kd_voucher = models.CharField(max_length=6)
    no_bukti = models.CharField(max_length=20)
    tanggal = models.DateTimeField()
    tanggal_jatuh_tempo = models.DateTimeField()
    status = models.CharField(max_length=1)
    diskon1 = models.FloatField()
    diskon2 = models.FloatField()
    diskon3 = models.FloatField()
    diskon4 = models.FloatField()
    diskon_uang = models.FloatField()
    pajak = models.FloatField()
    keterangan = models.CharField(max_length=50)
    kd_user = models.CharField(max_length=6)
    tanggal_server = models.DateTimeField(null=True, blank=True)
    tanggal_setor = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 't_penjualan'

class PenjualanDetail(SyncMetaMixin):
    no_transaksi = models.CharField(max_length=20)
    kd_barang = models.CharField(max_length=30)
    kd_satuan = models.CharField(max_length=6)
    kd_pegawai = models.CharField(max_length=6)
    jenis = models.CharField(max_length=1)
    diskon1 = models.FloatField()
    diskon2 = models.FloatField()
    diskon3 = models.FloatField()
    diskon4 = models.FloatField()
    harga_jual = models.DecimalField(max_digits=18, decimal_places=2)
    qty = models.FloatField()
    point1 = models.FloatField()
    point2 = models.FloatField()
    total = models.FloatField(null=True, blank=True)
    # No explicit PK found in schema, Django will add 'id' automatically or you need to define one.

    class Meta:
        db_table = 't_penjualan_detail'

class PenjualanDetailPegawai(SyncMetaMixin):
    no_transaksi = models.CharField(primary_key=True, max_length=20)
    kd_pegawai = models.CharField(max_length=6)

    class Meta:
        db_table = 't_penjualan_detail_pegawai'

class PenjualanJasa(SyncMetaMixin):
    no_transaksi = models.CharField(primary_key=True, max_length=20)
    kd_customer = models.CharField(max_length=20)
    kd_divisi = models.CharField(max_length=6)
    kd_jenis = models.CharField(max_length=6)
    kd_kas = models.CharField(max_length=6)
    kd_voucher = models.CharField(max_length=6)
    no_bukti = models.CharField(max_length=20)
    tanggal_pesan = models.DateTimeField()
    awal = models.DateTimeField()
    akhir = models.DateTimeField()
    status = models.CharField(max_length=1)
    diskon = models.FloatField()
    pajak = models.FloatField()
    services = models.FloatField(null=True, blank=True)
    other = models.FloatField()
    keterangan = models.CharField(max_length=50)
    kd_user = models.CharField(max_length=6)
    tanggal_server = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 't_penjualan_jasa'

class PenjualanJasaDetail(SyncMetaMixin):
    no_transaksi = models.CharField(primary_key=True, max_length=20)
    kd_pegawai = models.CharField(max_length=6)
    kd_jasa = models.CharField(max_length=6)
    qty = models.FloatField()
    harga = models.FloatField()
    diskon = models.DecimalField(max_digits=18, decimal_places=2)

    class Meta:
        db_table = 't_penjualan_jasa_detail'

class PenjualanKoin(SyncMetaMixin):
    ket = models.CharField(max_length=50)
    nominal = models.DecimalField(max_digits=18, decimal_places=2)
    qty = models.FloatField()
    # No explicit PK found in schema, Django will add 'id' automatically or you need to define one.

    class Meta:
        db_table = 't_penjualan_koin'

class PenjualanNotaKosong(SyncMetaMixin):
    no_transaksi = models.CharField(primary_key=True, max_length=20)
    keterangan = models.CharField(max_length=50)
    kd_user = models.CharField(max_length=6)
    tanggal_server = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 't_penjualan_nota_kosong'

class PenjualanOrder(SyncMetaMixin):
    no_order = models.CharField(primary_key=True, max_length=20)
    kd_customer = models.CharField(max_length=20)
    kd_divisi = models.CharField(max_length=6)
    kd_jenis = models.CharField(max_length=6)
    kd_kas = models.CharField(max_length=6)
    kd_voucher = models.CharField(max_length=6)
    no_bukti = models.CharField(max_length=20)
    tanggal = models.DateTimeField()
    tanggal_terima = models.DateTimeField()
    status = models.IntegerField()
    diskon1 = models.FloatField()
    diskon2 = models.FloatField()
    diskon3 = models.FloatField()
    diskon4 = models.FloatField()
    diskon_uang = models.FloatField()
    pajak = models.FloatField()
    keterangan = models.CharField(max_length=50)
    jaminan = models.DecimalField(max_digits=18, decimal_places=2)
    kd_user = models.CharField(max_length=10)
    tanggal_server = models.DateTimeField(null=True, blank=True)
    no_transaksi = models.CharField(null=True, blank=True, max_length=20)

    class Meta:
        db_table = 't_penjualan_order'

class PenjualanOrderDetail(SyncMetaMixin):
    no_order = models.CharField(primary_key=True, max_length=20)
    kd_barang = models.CharField(max_length=30)
    kd_satuan = models.CharField(max_length=6)
    kd_pegawai = models.CharField(max_length=10)
    jenis = models.IntegerField()
    diskon1 = models.FloatField()
    diskon2 = models.FloatField()
    diskon3 = models.FloatField()
    diskon4 = models.FloatField()
    harga_jual = models.DecimalField(max_digits=18, decimal_places=2)
    qty = models.FloatField()

    class Meta:
        db_table = 't_penjualan_order_detail'

class PenjualanPoint(SyncMetaMixin):
    no_transaksi = models.CharField(primary_key=True, max_length=20)
    kd_pegawai = models.CharField(max_length=6)
    tanggal = models.DateTimeField()
    jenis = models.CharField(max_length=1)
    awal = models.DateTimeField()
    akhir = models.DateTimeField()
    qty = models.FloatField()
    nominal = models.DecimalField(max_digits=18, decimal_places=2)
    lantai = models.IntegerField()
    divisi = models.CharField(max_length=6)
    kd_user = models.CharField(max_length=6)
    tanggal_server = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 't_penjualan_point'

class PenjualanRetur(SyncMetaMixin):
    no_retur = models.CharField(primary_key=True, max_length=20)
    kd_divisi = models.CharField(max_length=6)
    kd_customer = models.CharField(max_length=20)
    kd_jenis = models.CharField(max_length=6)
    kd_kas = models.CharField(max_length=6)
    tanggal = models.DateTimeField()
    no_bukti = models.CharField(max_length=20)
    diskon1 = models.FloatField()
    diskon2 = models.FloatField()
    diskon3 = models.FloatField()
    diskon4 = models.FloatField()
    pajak = models.FloatField()
    keterangan = models.CharField(max_length=50)
    kd_user = models.CharField(max_length=6)
    tanggal_server = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 't_penjualan_retur'

class PenjualanReturDetail(SyncMetaMixin):
    no_retur = models.CharField(max_length=20)
    kd_barang = models.CharField(max_length=30)
    kd_satuan = models.CharField(max_length=6)
    kd_pegawai = models.CharField(max_length=6)
    harga_jual = models.DecimalField(max_digits=18, decimal_places=2)
    qty = models.FloatField()
    diskon1 = models.FloatField()
    diskon2 = models.FloatField()
    diskon3 = models.FloatField()
    diskon4 = models.FloatField()
    # No explicit PK found in schema, Django will add 'id' automatically or you need to define one.

    class Meta:
        db_table = 't_penjualan_retur_detail'

class PenjualanSelected(SyncMetaMixin):
    no_transaksi = models.CharField(primary_key=True, max_length=20)
    tanggal = models.DateTimeField()
    total = models.DecimalField(max_digits=18, decimal_places=2)

    class Meta:
        db_table = 't_penjualan_selected'

class PenjualanTotal(SyncMetaMixin):
    no_transaksi = models.CharField(primary_key=True, max_length=20)
    total = models.DecimalField(max_digits=18, decimal_places=2)

    class Meta:
        db_table = 't_penjualan_total'

class PiutangCicilan(SyncMetaMixin):
    no_cicilan = models.CharField(primary_key=True, max_length=20)
    no_transaksi = models.CharField(max_length=20)
    kd_jenis = models.CharField(max_length=6)
    kd_pegawai = models.CharField(max_length=6)
    kd_kas = models.CharField(null=True, blank=True, max_length=6)
    nominal = models.DecimalField(max_digits=18, decimal_places=2)
    other = models.FloatField(null=True, blank=True)
    tanggal = models.DateTimeField()
    no_bukti = models.CharField(max_length=20)
    keterangan = models.CharField(max_length=50)
    kd_user = models.CharField(max_length=6)
    tanggal_server = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 't_piutang_cicilan'

class PiutangJasaCicilan(SyncMetaMixin):
    no_cicilan = models.CharField(primary_key=True, max_length=20)
    no_transaksi = models.CharField(max_length=20)
    kd_jenis = models.CharField(max_length=6)
    kd_pegawai = models.CharField(max_length=6)
    kd_kas = models.CharField(max_length=6)
    nominal = models.DecimalField(max_digits=18, decimal_places=2)
    other = models.FloatField()
    tanggal = models.DateTimeField()
    no_bukti = models.CharField(max_length=20)
    keterangan = models.CharField(max_length=50)
    kd_user = models.CharField(max_length=6)
    tanggal_server = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 't_piutang_jasa_cicilan'

class Prive(SyncMetaMixin):
    no_transaksi = models.CharField(primary_key=True, max_length=20)
    tanggal = models.DateTimeField()
    kd_kas = models.CharField(max_length=6)
    nominal = models.DecimalField(max_digits=18, decimal_places=2)
    keterangan = models.CharField(max_length=50)
    kd_user = models.CharField(max_length=6)

    class Meta:
        db_table = 't_prive'

class Sewa(SyncMetaMixin):
    no_transaksi = models.CharField(primary_key=True, max_length=20)
    tanggal = models.DateTimeField()
    kd_customer = models.CharField(max_length=6)
    awal = models.DateTimeField()
    akhir = models.DateTimeField()
    harga = models.FloatField()
    diskon1 = models.FloatField()
    diskon2 = models.FloatField()
    diskon3 = models.FloatField()
    diskon4 = models.FloatField()
    status = models.CharField(max_length=1)
    jenis = models.CharField(max_length=1)
    kd_item = models.CharField(max_length=6)

    class Meta:
        db_table = 't_sewa'

class SuratBerharga(SyncMetaMixin):
    no_surat_berharga = models.CharField(primary_key=True, max_length=20)
    kd_bank = models.CharField(max_length=6)
    kd_jenis = models.CharField(max_length=6)
    kd_pihak_lain = models.CharField(max_length=20)
    nominal = models.DecimalField(max_digits=18, decimal_places=2)
    tanggal_terima = models.DateTimeField()
    tanggal_jatuh_tempo = models.DateTimeField()
    tanggal_setor = models.DateTimeField(null=True, blank=True)
    tanggal_cair = models.DateTimeField(null=True, blank=True)
    kd_kas_setor = models.CharField(null=True, blank=True, max_length=6)
    status_asal = models.CharField(max_length=1)
    status_blong = models.CharField(max_length=1)
    keterangan = models.CharField(max_length=50)
    kd_user = models.CharField(max_length=6)
    tanggal_server = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 't_surat_berharga'

class Tagihan(SyncMetaMixin):
    no_tagihan = models.CharField(primary_key=True, max_length=20)
    kd_pegawai = models.CharField(max_length=6)
    keluar = models.DateTimeField()
    kembali = models.DateTimeField()
    kd_user = models.CharField(null=True, blank=True, max_length=6)
    tanggal_server = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 't_tagihan'

class TagihanDetail(SyncMetaMixin):
    no_tagihan = models.CharField(max_length=20)
    no_transaksi = models.CharField(max_length=20)
    status = models.CharField(max_length=1)
    keterangan = models.CharField(max_length=50)
    kembali = models.DateTimeField(null=True, blank=True)
    # No explicit PK found in schema, Django will add 'id' automatically or you need to define one.

    class Meta:
        db_table = 't_tagihan_detail'

class TransaksiBarang(SyncMetaMixin):
    no_transaksi = models.CharField(primary_key=True, max_length=20)
    kd_divisi = models.CharField(max_length=6)
    tanggal = models.DateTimeField()
    keterangan = models.CharField(max_length=50)
    no_nota = models.CharField(max_length=50)
    penerima = models.CharField(max_length=50)
    gudang = models.CharField(max_length=50)
    kd_user = models.CharField(max_length=6)
    jenis = models.CharField(max_length=1)

    class Meta:
        db_table = 't_transaksi_barang'

class TransaksiBarangDetail(SyncMetaMixin):
    no_transaksi = models.CharField(primary_key=True, max_length=20)
    kd_barang = models.CharField(max_length=30)
    kd_satuan = models.CharField(max_length=6)
    qty = models.FloatField()

    class Meta:
        db_table = 't_transaksi_barang_detail'

