from django.db import models
from app_core.models import ServerConfig

class SyncMetaMixin(models.Model):
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

class Agama(SyncMetaMixin):
    kd_agama = models.CharField(primary_key=True, max_length=6)
    nama = models.CharField(max_length=35)
    status = models.CharField(max_length=1)

    class Meta:
        db_table = 'm_agama'

class Aset(SyncMetaMixin):
    kd_aset = models.CharField(primary_key=True, max_length=6)
    kd_index = models.CharField(max_length=10)
    kd_supplier = models.CharField(max_length=6)
    kd_divisi = models.CharField(max_length=6)
    kd_kategori_aset = models.CharField(max_length=8)
    nama = models.CharField(max_length=35)
    tanggal_beli = models.DateTimeField()
    tanggal_habis_garansi = models.DateTimeField()
    harga_beli = models.DecimalField(max_digits=18, decimal_places=2)
    penyusutan = models.FloatField()
    nilai_residu = models.DecimalField(max_digits=18, decimal_places=2)
    keterangan = models.CharField(max_length=50)
    status = models.CharField(max_length=1)
    tanggal_jual = models.DateTimeField()
    kd_kas = models.CharField(max_length=6)
    kd_jenis = models.CharField(max_length=6)
    no_bukti = models.CharField(max_length=20)

    class Meta:
        db_table = 'm_aset'

class AsetKategori(SyncMetaMixin):
    kd_kategori_aset = models.CharField(primary_key=True, max_length=8)
    nama = models.CharField(max_length=35)
    keterangan = models.CharField(max_length=50)
    status = models.CharField(max_length=1)

    class Meta:
        db_table = 'm_aset_kategori'

class Bank(SyncMetaMixin):
    kd_bank = models.CharField(primary_key=True, max_length=6)
    nama = models.CharField(max_length=35)
    keterangan = models.CharField(max_length=50)
    status = models.CharField(max_length=1)

    class Meta:
        db_table = 'm_bank'

class Barang(SyncMetaMixin):
    kd_barang = models.CharField(primary_key=True, max_length=30)
    kd_kategori = models.CharField(max_length=6)
    kd_jenis_bahan = models.CharField(max_length=6)
    kd_model = models.CharField(max_length=6)
    kd_merk = models.CharField(max_length=6)
    kd_warna = models.CharField(max_length=6)
    ukuran = models.FloatField()
    nama = models.CharField(null=True, blank=True, max_length=50)
    keterangan = models.CharField(max_length=50)
    status = models.CharField(max_length=1)
    status_pinjam = models.CharField(max_length=1)
    pabrik = models.CharField(max_length=1)
    tanggal_daftar = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'm_barang'

class BarangDivisi(SyncMetaMixin):
    kd_divisi = models.CharField(primary_key=True, max_length=6)
    kd_barang = models.CharField(max_length=30)
    stok_awal = models.FloatField()
    harga_beli_awal = models.DecimalField(max_digits=18, decimal_places=2)
    stok_min = models.FloatField()
    status = models.CharField(max_length=1)
    point = models.FloatField(null=True, blank=True)

    class Meta:
        db_table = 'm_barang_divisi'

class BarangDivisiDiskon(SyncMetaMixin):
    kd_divisi = models.CharField(primary_key=True, max_length=6)
    kd_barang = models.CharField(max_length=30)
    kd_satuan = models.CharField(max_length=6)
    qty_minim = models.FloatField()
    diskon1 = models.FloatField()
    diskon2 = models.FloatField()
    diskon3 = models.FloatField()
    diskon4 = models.FloatField()

    class Meta:
        db_table = 'm_barang_divisi_diskon'

class BarangFormula(SyncMetaMixin):
    nomor = models.CharField(primary_key=True, max_length=50)
    kd_barang = models.CharField(max_length=30)
    kd_satuan = models.CharField(max_length=6)
    qty = models.FloatField()
    keterangan = models.CharField(max_length=200)

    class Meta:
        db_table = 'm_barang_formula'

class BarangGambar(SyncMetaMixin):
    kd_barang = models.CharField(primary_key=True, max_length=30)
    nomor = models.IntegerField()
    keterangan = models.CharField(max_length=300)
    gambar = models.CharField(max_length=600)
    ismain = models.IntegerField()
    spesifikasi = models.CharField(null=True, blank=True, max_length=2000)
    deskripsi = models.CharField(null=True, blank=True, max_length=1000)

    class Meta:
        db_table = 'm_barang_gambar'

class BarangPromo(SyncMetaMixin):
    kd_promo = models.CharField(primary_key=True, max_length=50)
    kd_divisi = models.CharField(max_length=6)
    tanggal_input = models.DateTimeField()
    tanggal_awal = models.DateTimeField()
    jam_awal = models.DateTimeField()
    tanggal_akhir = models.DateTimeField()
    jam_akhir = models.DateTimeField()
    keterangan = models.CharField(max_length=200)
    kd_user = models.CharField(max_length=6)
    tanggal_server = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'm_barang_promo'

class BarangPromoDetail(SyncMetaMixin):
    kd_promo = models.CharField(primary_key=True, max_length=50)
    kd_barang = models.CharField(max_length=30)
    kd_satuan = models.CharField(max_length=6)
    qty_minim = models.FloatField()
    harga = models.CharField(max_length=10)
    diskon1 = models.FloatField()
    diskon2 = models.FloatField()
    diskon3 = models.FloatField()
    diskon4 = models.FloatField()
    harga_bersih = models.FloatField(null=True, blank=True)

    class Meta:
        db_table = 'm_barang_promo_detail'

class BarangSatuan(SyncMetaMixin):
    kd_barang = models.CharField(primary_key=True, max_length=30)
    kd_satuan = models.CharField(max_length=6)
    jumlah = models.FloatField()
    harga_jual = models.DecimalField(max_digits=18, decimal_places=2)
    status = models.CharField(max_length=1)
    margin = models.FloatField(null=True, blank=True)

    class Meta:
        db_table = 'm_barang_satuan'

class BarangSewa(SyncMetaMixin):
    kd_item = models.CharField(primary_key=True, max_length=6)
    kd_jenis_item = models.CharField(null=True, blank=True, max_length=6)
    nama = models.CharField(null=True, blank=True, max_length=35)
    harga = models.DecimalField(null=True, blank=True, max_digits=18, decimal_places=2)
    diskon = models.FloatField(null=True, blank=True)
    keterangan = models.CharField(null=True, blank=True, max_length=50)
    status = models.CharField(null=True, blank=True, max_length=1)

    class Meta:
        db_table = 'm_barang_sewa'

class BarangSewaJenis(SyncMetaMixin):
    kd_jenis_item = models.CharField(primary_key=True, max_length=6)
    nama = models.CharField(null=True, blank=True, max_length=35)
    harga = models.DecimalField(null=True, blank=True, max_digits=18, decimal_places=2)
    diskon = models.FloatField(null=True, blank=True)
    keterangan = models.CharField(null=True, blank=True, max_length=50)
    status = models.CharField(null=True, blank=True, max_length=1)

    class Meta:
        db_table = 'm_barang_sewa_jenis'

class BarangStokAkhir(SyncMetaMixin):
    kd_divisi = models.CharField(primary_key=True, max_length=6)
    kd_barang = models.CharField(max_length=30)
    stok_akhir = models.FloatField()

    class Meta:
        db_table = 'm_barang_stok_akhir'

class BarangSupplier(SyncMetaMixin):
    kd_supplier = models.CharField(primary_key=True, max_length=6)
    kd_barang = models.CharField(max_length=30)
    status = models.CharField(max_length=1)

    class Meta:
        db_table = 'm_barang_supplier'

class Biaya(SyncMetaMixin):
    kd_biaya = models.CharField(primary_key=True, max_length=6)
    kd_index = models.CharField(null=True, blank=True, max_length=10)
    nama = models.CharField(max_length=35)
    keterangan = models.CharField(max_length=50)
    status = models.CharField(max_length=1)

    class Meta:
        db_table = 'm_biaya'

class Customer(SyncMetaMixin):
    kd_customer = models.CharField(primary_key=True, max_length=20)
    kd_kota = models.CharField(max_length=6)
    nama = models.CharField(max_length=35)
    alamat = models.CharField(max_length=50)
    telepon = models.CharField(max_length=10)
    fax = models.CharField(max_length=10)
    kontak = models.CharField(max_length=35)
    hp = models.CharField(max_length=15)
    email = models.CharField(max_length=30)
    point = models.DecimalField(max_digits=18, decimal_places=2)
    limit_kredit = models.DecimalField(max_digits=18, decimal_places=2)
    disc = models.FloatField()
    status = models.CharField(max_length=1)
    parent = models.CharField(max_length=50)
    keterangan = models.CharField(max_length=200)
    npwp_no = models.CharField(max_length=50)
    nppkp_no = models.CharField(max_length=50)
    npwp_nama = models.CharField(max_length=50)
    npwp_alamat = models.CharField(max_length=500)

    class Meta:
        db_table = 'm_customer'

class Divisi(SyncMetaMixin):
    kd_divisi = models.CharField(primary_key=True, max_length=6)
    nama = models.CharField(max_length=35)
    kepala_nota = models.CharField(max_length=5)
    keterangan = models.CharField(max_length=50)
    status = models.CharField(max_length=1)

    class Meta:
        db_table = 'm_divisi'

class Ekspedisi(SyncMetaMixin):
    kd_ekspedisi = models.CharField(primary_key=True, max_length=6)
    kd_kota = models.CharField(max_length=6)
    nama = models.CharField(max_length=35)
    alamat = models.CharField(max_length=50)
    telepon = models.CharField(max_length=10)
    fax = models.CharField(max_length=10)
    kontak = models.CharField(max_length=35)
    hp = models.CharField(max_length=15)
    email = models.CharField(max_length=30)
    kd_bank = models.CharField(max_length=6)
    rekening = models.CharField(max_length=25)
    status = models.CharField(max_length=1)

    class Meta:
        db_table = 'm_ekspedisi'

class HariLibur(SyncMetaMixin):
    kd_hari_libur = models.CharField(primary_key=True, max_length=6)
    tanggal = models.DateTimeField()
    keterangan = models.CharField(max_length=50)
    status = models.CharField(max_length=1)

    class Meta:
        db_table = 'm_hari_libur'

class HariLiburAgama(SyncMetaMixin):
    kd_agama = models.CharField(primary_key=True, max_length=6)
    kd_hari_libur = models.CharField(max_length=6)
    status = models.CharField(max_length=1)

    class Meta:
        db_table = 'm_hari_libur_agama'

class Jabatan(SyncMetaMixin):
    kd_jabatan = models.CharField(primary_key=True, max_length=6)
    nama = models.CharField(max_length=35)
    keterangan = models.CharField(max_length=50)
    status = models.CharField(max_length=1)
    uang_makan = models.DecimalField(max_digits=18, decimal_places=2)

    class Meta:
        db_table = 'm_jabatan'

class JabatanDetail(SyncMetaMixin):
    kd_jabatan = models.CharField(primary_key=True, max_length=6)
    kd_gaji = models.CharField(max_length=6)
    status = models.CharField(max_length=1)

    class Meta:
        db_table = 'm_jabatan_detail'

class JabatanGaji(SyncMetaMixin):
    kd_gaji = models.CharField(primary_key=True, max_length=6)
    nama = models.CharField(max_length=35)
    gaji_pokok = models.DecimalField(max_digits=18, decimal_places=2)
    tunjangan = models.DecimalField(max_digits=18, decimal_places=2)
    lain_lain = models.DecimalField(max_digits=18, decimal_places=2)
    status = models.CharField(max_length=1)

    class Meta:
        db_table = 'm_jabatan_gaji'

class JamKerja(SyncMetaMixin):
    kd_shift = models.CharField(primary_key=True, max_length=6)
    nama = models.CharField(max_length=35)
    masuk_senin = models.DateTimeField()
    masuk_selasa = models.DateTimeField()
    masuk_rabu = models.DateTimeField()
    masuk_kamis = models.DateTimeField()
    masuk_jumat = models.DateTimeField()
    masuk_sabtu = models.DateTimeField()
    masuk_minggu = models.DateTimeField()
    mulai_istirahat_senin = models.DateTimeField()
    selesai_istirahat_senin = models.DateTimeField()
    mulai_istirahat_selasa = models.DateTimeField()
    selesai_istirahat_selasa = models.DateTimeField()
    mulai_istirahat_rabu = models.DateTimeField()
    selesai_istirahat_rabu = models.DateTimeField()
    mulai_istirahat_kamis = models.DateTimeField()
    selesai_istirahat_kamis = models.DateTimeField()
    mulai_istirahat_jumat = models.DateTimeField()
    selesai_istirahat_jumat = models.DateTimeField()
    mulai_istirahat_sabtu = models.DateTimeField()
    selesai_istirahat_sabtu = models.DateTimeField()
    mulai_istirahat_minggu = models.DateTimeField()
    selesai_istirahat_minggu = models.DateTimeField()
    pulang_senin = models.DateTimeField()
    pulang_selasa = models.DateTimeField()
    pulang_rabu = models.DateTimeField()
    pulang_kamis = models.DateTimeField()
    pulang_jumat = models.DateTimeField()
    pulang_sabtu = models.DateTimeField()
    pulang_minggu = models.DateTimeField()
    status = models.CharField(max_length=1)
    keterangan = models.CharField(max_length=200)

    class Meta:
        db_table = 'm_jam_kerja'

class Jasa(SyncMetaMixin):
    kd_jasa = models.CharField(primary_key=True, max_length=6)
    kd_jasa_kategori = models.CharField(max_length=6)
    nama = models.CharField(max_length=35)
    harga = models.DecimalField(max_digits=18, decimal_places=2)
    diskon = models.FloatField()
    keterangan = models.CharField(max_length=50)
    status = models.CharField(max_length=1)
    tanggal_daftar = models.DateTimeField()

    class Meta:
        db_table = 'm_jasa'

class JasaDetail(SyncMetaMixin):
    kd_jasa = models.CharField(primary_key=True, max_length=6)
    kd_barang = models.CharField(max_length=30)
    kd_satuan = models.CharField(max_length=6)
    qty = models.FloatField()
    status = models.CharField(max_length=1)

    class Meta:
        db_table = 'm_jasa_detail'

class JasaKategori(SyncMetaMixin):
    kd_jasa_kategori = models.CharField(primary_key=True, max_length=6)
    nama = models.CharField(max_length=35)
    diskon = models.FloatField()
    keterangan = models.CharField(max_length=50)
    status = models.CharField(max_length=1)

    class Meta:
        db_table = 'm_jasa_kategori'

class JenisBahan(SyncMetaMixin):
    kd_jenis_bahan = models.CharField(primary_key=True, max_length=6)
    nama = models.CharField(max_length=35)
    keterangan = models.CharField(max_length=50)
    status = models.CharField(max_length=1)

    class Meta:
        db_table = 'm_jenis_bahan'

class JenisBayar(SyncMetaMixin):
    kd_jenis = models.CharField(primary_key=True, max_length=6)
    nama = models.CharField(max_length=35)
    setting = models.CharField(max_length=50)
    other = models.FloatField()
    keterangan = models.CharField(max_length=50)
    status = models.CharField(max_length=1)

    class Meta:
        db_table = 'm_jenis_bayar'

class JenisIzin(SyncMetaMixin):
    kd_izin = models.CharField(primary_key=True, max_length=6)
    nama = models.CharField(max_length=35)
    keterangan = models.CharField(max_length=50)
    status = models.CharField(max_length=1)

    class Meta:
        db_table = 'm_jenis_izin'

class JenisPerawatan(SyncMetaMixin):
    kd_jenis_perawatan = models.CharField(primary_key=True, max_length=8)
    jenis_perawatan = models.CharField(max_length=50)
    keterangan = models.CharField(max_length=50)
    status = models.CharField(max_length=1)

    class Meta:
        db_table = 'm_jenis_perawatan'

class JenisSurat(SyncMetaMixin):
    kd_jenis_surat = models.CharField(primary_key=True, max_length=6)
    nama = models.CharField(max_length=35)
    keterangan = models.CharField(max_length=50)
    status = models.CharField(max_length=1)

    class Meta:
        db_table = 'm_jenis_surat'

class Jurnal(SyncMetaMixin):
    kd_index = models.CharField(primary_key=True, max_length=10)
    kd_akun = models.CharField(max_length=10)
    nama = models.CharField(max_length=50)
    keterangan = models.CharField(null=True, blank=True, max_length=50)
    status_neraca = models.CharField(null=True, blank=True, max_length=1)
    status = models.CharField(max_length=1)

    class Meta:
        db_table = 'm_jurnal'

class Kas(SyncMetaMixin):
    kd_kas = models.CharField(primary_key=True, max_length=6)
    kd_index = models.CharField(max_length=10)
    no_rekening = models.CharField(max_length=25)
    kd_bank = models.CharField(max_length=6)
    kd_kota = models.CharField(max_length=6)
    telepon = models.CharField(max_length=10)
    kontak = models.CharField(max_length=35)
    cabang = models.CharField(max_length=50)
    saldo_awal = models.DecimalField(max_digits=18, decimal_places=2)
    keterangan = models.CharField(max_length=50)
    status = models.CharField(max_length=1)

    class Meta:
        db_table = 'm_kas'

class Kategori(SyncMetaMixin):
    kd_kategori = models.CharField(primary_key=True, max_length=6)
    nama = models.CharField(max_length=35)
    keterangan = models.CharField(max_length=50)
    status = models.CharField(max_length=1)

    class Meta:
        db_table = 'm_kategori'

class Kendaraan(SyncMetaMixin):
    no_STNK = models.CharField(primary_key=True, max_length=15)
    jenis = models.CharField(max_length=35)
    nomor_KIR = models.CharField(max_length=15)
    tahun = models.CharField(max_length=4)
    oli_mesin = models.FloatField()
    keterangan = models.CharField(max_length=50)
    status = models.CharField(max_length=1)

    class Meta:
        db_table = 'm_kendaraan'

class Kota(SyncMetaMixin):
    kd_kota = models.CharField(primary_key=True, max_length=6)
    kd_telp = models.CharField(null=True, blank=True, max_length=4)
    kd_negara = models.CharField(max_length=3)
    nama = models.CharField(max_length=35)
    status = models.CharField(max_length=1)

    class Meta:
        db_table = 'm_kota'

class Merk(SyncMetaMixin):
    kd_merk = models.CharField(primary_key=True, max_length=6)
    nama = models.CharField(max_length=35)
    status = models.CharField(max_length=1)
    keterangan = models.CharField(max_length=50)

    class Meta:
        db_table = 'm_merk'

class Model(SyncMetaMixin):
    kd_model = models.CharField(primary_key=True, max_length=6)
    nama = models.CharField(max_length=35)
    status = models.CharField(max_length=1)
    keterangan = models.CharField(max_length=50)

    class Meta:
        db_table = 'm_model'

class Negara(SyncMetaMixin):
    kd_negara = models.CharField(primary_key=True, max_length=3)
    nama = models.CharField(max_length=35)
    status = models.CharField(max_length=1)

    class Meta:
        db_table = 'm_negara'

class Pegawai(SyncMetaMixin):
    kd_pegawai = models.CharField(primary_key=True, max_length=6)
    kd_jabatan = models.CharField(max_length=6)
    kd_jenis = models.CharField(max_length=6)
    kd_kota = models.CharField(max_length=6)
    kd_agama = models.CharField(max_length=6)
    kd_shift = models.CharField(max_length=6)
    kd_divisi = models.CharField(max_length=6)
    nama = models.CharField(max_length=35)
    tempat_lahir = models.CharField(max_length=35)
    tanggal_lahir = models.DateTimeField()
    alamat = models.CharField(max_length=50)
    telepon = models.CharField(max_length=10)
    hp = models.CharField(max_length=15)
    ktp = models.CharField(max_length=20)
    tgl_masuk = models.DateTimeField()
    kelamin = models.CharField(max_length=1)
    foto = models.BinaryField(null=True, blank=True)
    kelompok = models.IntegerField()
    point = models.IntegerField()
    keterangan = models.CharField(max_length=50)
    status_kawin = models.CharField(max_length=1)
    status = models.CharField(max_length=1)
    status_lembur = models.CharField(max_length=1)

    class Meta:
        db_table = 'm_pegawai'

class PegawaiFingerPrint(SyncMetaMixin):
    kd_pegawai = models.CharField(primary_key=True, max_length=6)
    kd_finger = models.IntegerField()
    keterangan = models.CharField(max_length=50)
    status = models.CharField(max_length=1)

    class Meta:
        db_table = 'm_pegawai_finger_print'

class PegawaiJenis(SyncMetaMixin):
    kd_jenis = models.CharField(primary_key=True, max_length=6)
    nama = models.CharField(max_length=35)
    keterangan = models.CharField(max_length=50)
    status = models.CharField(max_length=1)

    class Meta:
        db_table = 'm_pegawai_jenis'

class PegawaiKomisi(SyncMetaMixin):
    kd_pegawai = models.CharField(primary_key=True, max_length=6)
    kd_barang = models.CharField(max_length=30)
    kd_satuan = models.CharField(max_length=6)
    komisi = models.DecimalField(max_digits=18, decimal_places=2)
    status = models.CharField(max_length=1)

    class Meta:
        db_table = 'm_pegawai_komisi'

class Pendapatan(SyncMetaMixin):
    kd_pendapatan = models.CharField(primary_key=True, max_length=6)
    kd_index = models.CharField(max_length=10)
    nama = models.CharField(max_length=35)
    keterangan = models.CharField(max_length=50)
    status = models.CharField(max_length=1)

    class Meta:
        db_table = 'm_pendapatan'

class Satuan(SyncMetaMixin):
    kd_satuan = models.CharField(primary_key=True, max_length=6)
    nama = models.CharField(max_length=35)
    keterangan = models.CharField(max_length=50)
    status = models.CharField(max_length=1)

    class Meta:
        db_table = 'm_satuan'

class Supplier(SyncMetaMixin):
    kd_supplier = models.CharField(primary_key=True, max_length=6)
    kd_kota = models.CharField(max_length=6)
    nama = models.CharField(max_length=35)
    alamat = models.CharField(max_length=50)
    telepon = models.CharField(max_length=10)
    fax = models.CharField(max_length=10)
    kontak = models.CharField(max_length=35)
    hp = models.CharField(max_length=15)
    email = models.CharField(max_length=30)
    kd_bank = models.CharField(max_length=6)
    rekening = models.CharField(max_length=25)
    jenis = models.CharField(max_length=1)
    keterangan = models.CharField(max_length=50)

    class Meta:
        db_table = 'm_supplier'

class Surat(SyncMetaMixin):
    kd_surat = models.CharField(primary_key=True, max_length=50)
    kd_jenis_surat = models.CharField(max_length=6)
    prihal = models.CharField(max_length=50)
    lampiran = models.CharField(max_length=50)
    tanggal_buat = models.DateTimeField()
    tanggal_perpanjangan = models.DateTimeField()
    instansi = models.CharField(max_length=50)
    biaya = models.DecimalField(max_digits=18, decimal_places=2)
    keterangan = models.CharField(max_length=50)
    status = models.CharField(max_length=1)
    kd_user = models.CharField(max_length=6)
    tanggal_server = models.DateTimeField()

    class Meta:
        db_table = 'm_surat'

class Userx(SyncMetaMixin):
    kd_user = models.CharField(primary_key=True, max_length=6)
    kd_group = models.CharField(max_length=6)
    nama = models.CharField(max_length=35)
    passwd = models.CharField(max_length=35)
    keterangan = models.CharField(max_length=50)
    status = models.CharField(max_length=1)
    m_UserLevels = models.IntegerField(null=True, blank=True)
    passweb = models.CharField(null=True, blank=True, max_length=128)

    class Meta:
        db_table = 'm_userx'

class Voucher(SyncMetaMixin):
    kd_voucher = models.CharField(primary_key=True, max_length=6)
    nama = models.CharField(max_length=35)
    nominal = models.FloatField()
    keterangan = models.CharField(max_length=50)
    status = models.CharField(max_length=1)

    class Meta:
        db_table = 'm_voucher'

class Warna(SyncMetaMixin):
    kd_warna = models.CharField(primary_key=True, max_length=6)
    nama = models.CharField(max_length=35)
    status = models.CharField(max_length=1)
    keterangan = models.CharField(max_length=50)

    class Meta:
        db_table = 'm_warna'

class TutupBuku(SyncMetaMixin):
    periode = models.IntegerField(primary_key=True)
    tanggal = models.DateTimeField()

    class Meta:
        db_table = 'g_tutup_buku'

