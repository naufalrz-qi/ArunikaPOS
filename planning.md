# Implementation Plan: GrosirPusat Data Sync System
> Versi: 1.2 — Revisi aturan Gudang: hanya `m_barang` dan `m_customer` yang dijadikan acuan master dari Gudang

---

## Gambaran Sistem

Sistem ini berfungsi sebagai **jembatan data terpusat** yang menarik, memvalidasi, dan menyinkronkan data dari beberapa SQL Server (MSSQL) ke satu database PostgreSQL lokal. Seluruh kendali operasional berjalan lewat antarmuka web — tidak ada akses terminal yang diperlukan oleh operator.

### Arsitektur Multi-Server

```
┌─────────────────────────────────────────────────────────┐
│                   MSSQL Servers (Sumber)                 │
│  ┌───────────┐   ┌───────────┐   ┌─────────────────┐   │
│  │  Gudang   │   │  Grosir   │   │     Retail      │   │
│  │ (master   │   │ (harga    │   │  (harga sendiri)│   │
│  │ m_barang  │   │  sendiri) │   │                 │   │
│  │+m_customer│   │           │   │                 │   │
│  └─────┬─────┘   └─────┬─────┘   └────────┬────────┘   │
└────────┼───────────────┼──────────────────┼────────────┘
         │               │                  │
         ▼               ▼                  ▼
┌─────────────────────────────────────────────────────────┐
│              Django + Celery (Aplikasi Lokal)            │
│  ┌───────────┐  ┌──────────────┐  ┌──────────────────┐ │
│  │ ETL Core  │  │ Celery Tasks │  │ Web Control Panel│ │
│  │ (app_sync)│  │  + Beat      │  │   (app_core)     │ │
│  └─────┬─────┘  └──────┬───────┘  └──────────────────┘ │
│        └───────────────┘                                 │
│                   ▼                                      │
│  ┌───────────────────────────┐   ┌──────────────────┐  │
│  │     PostgreSQL (Lokal)    │   │   Redis (Broker)  │  │
│  │  - Data Master & Transaksi│   │  - Task Queue     │  │
│  │  - Log Sync               │   │  - Progress State │  │
│  │  - Config Server          │   │                   │  │
│  └───────────────────────────┘   └──────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

### Aturan Bisnis Inti
| Aturan | Detail |
|---|---|
| **Acuan dari Gudang** | Hanya `m_barang` dan `m_customer` yang menjadikan Gudang sebagai sumber kebenaran utama. Tabel lain di-sync dari masing-masing server (grosir/retail) sendiri-sendiri. |
| **Barang Baru dari Grosir/Retail** | Jika ada `kd_barang` yang belum ada di Gudang, tetap didaftarkan ke DB lokal dengan penanda server asal. |
| **Manajemen Harga** | Harga `m_barang_satuan.harga_jual` dan `m_barang_divisi_diskon` TIDAK disamakan otomatis. Setiap server punya harga masing-masing. |
| **Sync Harga** | Hanya bisa dilakukan manual via web, dengan fitur checklist per-barang. |
| **Referensi Waktu Sync** | Kolom `tanggal_server` dipakai untuk incremental sync pada tabel transaksi. |

---

## Analisis Skema Database

Berdasarkan `strukturdatabase_GrosirPusat.txt`, tabel dikelompokkan sebagai berikut:

### Kelompok Tabel berdasarkan Prioritas Sync

#### Tier 1 — Data Inti Barang (Sync Wajib, Prioritas Tertinggi)
```
m_barang            → Master barang (kd_barang = PK utama)
                      ⚠ Acuan dari Gudang — sync Gudang DULU, baru Grosir/Retail
m_barang_satuan     → Satuan & harga jual per satuan (TIDAK di-sync otomatis, per-server)
m_barang_divisi     → Stok & harga awal per divisi
m_barang_divisi_diskon → Aturan diskon per barang (per-server, tidak auto-sync)
m_kategori          → Kategori barang
m_satuan            → Master satuan ukuran
m_merk              → Master merek
m_warna             → Master warna
m_model             → Master model
m_jenis_bahan       → Master jenis bahan
m_barang_stok_akhir → Snapshot stok akhir per divisi
```

#### Tier 2 — Mitra Bisnis (Sync Penting)
```
m_customer          → Data pelanggan (kd_customer = varchar 20)
                      ⚠ Acuan dari Gudang — sync Gudang DULU, baru Grosir/Retail
m_supplier          → Data supplier
m_ekspedisi         → Data ekspedisi/pengiriman
m_kota              → Master kota
m_negara            → Master negara
m_bank              → Master bank
m_kas               → Akun kas/bank
```

#### Tier 3 — Data Transaksi (Incremental Sync via tanggal_server)
```
t_penjualan + t_penjualan_detail        → Transaksi penjualan
t_pembelian + t_pembelian_detail        → Transaksi pembelian
t_penjualan_retur + _detail             → Retur penjualan
t_pembelian_retur + _detail             → Retur pembelian
t_penjualan_order + _detail             → Order penjualan
t_pembelian_order + _detail             → Order pembelian
t_mutasi_stok + t_mutasi_stok_detail    → Mutasi stok antar divisi
t_opname_stok                           → Stock opname
t_piutang_cicilan                       → Cicilan piutang
t_hutang_cicilan                        → Cicilan hutang
t_biaya_operasional                     → Biaya operasional
t_pendapatan                            → Pendapatan lain-lain
t_mutasi_kas                            → Mutasi kas
```

#### Tier 4 — SDM & Operasional (Sync Opsional)
```
m_pegawai + m_pegawai_jenis             → Data karyawan
m_jabatan + m_jabatan_detail            → Jabatan & gaji
m_jam_kerja                             → Shift kerja
t_absensi                               → Absensi
t_gaji                                  → Penggajian
t_pegawai_izin                          → Izin karyawan
t_kendaraan_*                           → Data & operasional kendaraan
m_aset + m_aset_kategori                → Aset perusahaan
```

### Tabel dengan `tanggal_server` (Mendukung Incremental/Auto Sync)

> Kolom ini adalah kunci utama untuk **Auto Sync** — query cukup `WHERE tanggal_server > last_sync_time`.

```
Transaksi Utama:
  t_pembelian, t_penjualan, t_penjualan_jasa
  t_pembelian_order, t_penjualan_order
  t_pembelian_retur, t_penjualan_retur
  t_mutasi_stok, t_mutasi_kas
  t_opname_stok, t_pemakaian_barang
  t_piutang_cicilan, t_piutang_jasa_cicilan
  t_hutang_cicilan, t_hutang_aset_cicilan
  t_biaya_operasional, t_pendapatan
  t_surat_berharga, t_tagihan
  t_penjualan_nota_kosong, t_penjualan_point

SDM & Lainnya:
  t_absensi, t_pegawai_izin, t_pegawai_surat_peringatan
  t_hutang_pegawai, t_hutang_pegawai_cicilan
  t_kendaraan_jarak_tempuh, t_kendaraan_pengisian_bbm
  m_barang_promo, m_surat
```

### Tabel TANPA `tanggal_server` (Perlu Strategi Khusus)
```
Semua tabel m_ master (m_barang, m_kategori, m_customer, dll.)
Detail transaksi (t_penjualan_detail, t_pembelian_detail, dll.)
→ Strategi: Hash checksum per baris ATAU full-replace per PK
```

---

## Titik Awal (Starting Point) — Yang Dibangun Pertama

Sebelum masuk fase-fase besar, deliverable MVP pertama adalah:

```
✅ 1. Auth (Login/Logout)
✅ 2. Dashboard (halaman utama, statistik dasar)
✅ 3. Kelola Server (CRUD koneksi MSSQL: gudang, grosir, retail)
✅ 4. Kelola User (CRUD pengguna sistem)
✅ 5. Tampilan Data Master: m_barang dan m_kategori (read-only, dengan pagination)
```

---

## Fase-Fase Pengembangan

---

### Fase 0: Starting Point & Fondasi (Minggu 1)

**Tujuan:** Aplikasi bisa login, punya dashboard, dan bisa menyimpan konfigurasi server.

#### 0.1 Setup Proyek Django

```bash
# Struktur folder proyek
grosirpusat_sync/
├── grosirpusat_sync/   # settings, urls, celery.py, wsgi.py
├── app_core/           # dashboard, auth, UI umum, server config, user mgmt
├── app_master/         # models & views untuk tabel m_ (barang, customer, dll.)
├── app_transaksi/      # models & views untuk tabel t_ (penjualan, pembelian, dll.)
├── app_sync/           # seluruh logika ETL, Celery tasks, reconciliation
└── templates/          # HTML templates (base.html, dashboard, dll.)
```

```bash
# Instalasi paket minimum untuk fase ini
pip install django
pip install psycopg2-binary          # Driver PostgreSQL
pip install pyodbc                   # Driver SQL Server
pip install mssql-django             # atau django-pyodbc-azure
pip install celery redis             # Task queue
pip install django-celery-results    # Simpan hasil task di DB
pip install django-celery-beat       # Penjadwal periodik
pip install cryptography             # Untuk enkripsi password server di DB
```

#### 0.2 Konfigurasi `settings.py`

```python
DATABASES = {
    # Database utama Django (PostgreSQL)
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'grosirpusat_local',
        'USER': 'pguser',
        'PASSWORD': '...',
        'HOST': 'localhost',
        'PORT': '5432',
    }
    # MSSQL server TIDAK didefinisikan di sini secara statis.
    # Koneksi dibangun secara dinamis dari data tabel ServerConfig
    # menggunakan pyodbc langsung (lihat Fase 2).
}

CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'django-db'
CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers:DatabaseScheduler'
```

#### 0.3 Model Awal untuk Fase Ini (`app_core/models.py`)

```python
from django.db import models
from cryptography.fernet import Fernet

class ServerConfig(models.Model):
    """Menyimpan konfigurasi koneksi MSSQL."""

    SERVER_TYPES = [
        ('gudang',  'Gudang'),
        ('grosir',  'Grosir'),
        ('retail',  'Retail'),
    ]

    nama        = models.CharField(max_length=100)
    tipe        = models.CharField(max_length=20, choices=SERVER_TYPES)
    host        = models.CharField(max_length=255)
    port        = models.IntegerField(default=1433)
    db_name     = models.CharField(max_length=100)
    username    = models.CharField(max_length=100)
    password    = models.BinaryField()     # Disimpan terenkripsi (Fernet)
    is_active   = models.BooleanField(default=True)
    keterangan  = models.TextField(blank=True)
    dibuat_pada = models.DateTimeField(auto_now_add=True)
    diubah_pada = models.DateTimeField(auto_now=True)

    def get_connection_string(self) -> str:
        """Mengembalikan connection string pyodbc."""
        pwd = Fernet(settings.SECRET_KEY_BYTES).decrypt(self.password).decode()
        return (
            f"DRIVER={{ODBC Driver 17 for SQL Server}};"
            f"SERVER={self.host},{self.port};"
            f"DATABASE={self.db_name};"
            f"UID={self.username};PWD={pwd};"
        )

    def __str__(self):
        return f"{self.nama} ({self.tipe})"


class SyncLog(models.Model):
    """Log setiap eksekusi sync."""

    JENIS_SYNC = [
        ('full_sync',    'Full Sync'),
        ('auto_sync',    'Auto Sync'),
        ('monthly_check','Monthly Check'),
        ('yearly_check', 'Yearly Check'),
        ('full_check',   'Full Check'),
        ('price_sync',   'Price Sync'),
    ]
    STATUS = [
        ('running',  'Berjalan'),
        ('success',  'Sukses'),
        ('failed',   'Gagal'),
        ('partial',  'Sebagian'),
    ]

    server          = models.ForeignKey(ServerConfig, on_delete=models.SET_NULL, null=True)
    jenis           = models.CharField(max_length=30, choices=JENIS_SYNC)
    status          = models.CharField(max_length=20, choices=STATUS, default='running')
    tabel           = models.CharField(max_length=100, blank=True)   # nama tabel yang di-sync
    celery_task_id  = models.CharField(max_length=255, blank=True)
    total_data      = models.BigIntegerField(default=0)
    data_baru       = models.IntegerField(default=0)
    data_diupdate   = models.IntegerField(default=0)
    data_error      = models.IntegerField(default=0)
    progress_pct    = models.FloatField(default=0.0)   # 0-100
    pesan_error     = models.TextField(blank=True)
    mulai_pada      = models.DateTimeField(auto_now_add=True)
    selesai_pada    = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-mulai_pada']
```

#### 0.4 Halaman-halaman Fase 0

| Halaman | URL | Deskripsi |
|---|---|---|
| Login | `/login/` | Form login standar Django |
| Dashboard | `/` | Statistik ringkas, status sync terakhir per server |
| Kelola Server | `/server/` | CRUD ServerConfig, tombol "Test Koneksi" |
| Kelola User | `/user/` | CRUD user Django (`auth.User`) |
| Data Barang | `/master/barang/` | Tabel paginasi `m_barang` dari PostgreSQL |
| Data Kategori | `/master/kategori/` | Tabel paginasi `m_kategori` dari PostgreSQL |

---

### Fase 1: Desain Model Database Lengkap (Minggu 1–2)

**Tujuan:** Semua tabel dari `strukturdatabase_GrosirPusat.txt` yang diprioritaskan sudah punya Django model di PostgreSQL.

#### 1.1 Strategi Penamaan Model

Semua model lokal di PostgreSQL **menambahkan kolom metadata sync** di luar kolom asli MSSQL:

```python
class SyncMetaMixin(models.Model):
    """Mixin untuk metadata sinkronisasi, ditambahkan ke semua model sync."""
    _sync_server    = models.ForeignKey('app_core.ServerConfig',
                                        on_delete=models.SET_NULL, null=True,
                                        db_column='_sync_server_id')
    _sync_created   = models.DateTimeField(auto_now_add=True, db_column='_sync_created')
    _sync_updated   = models.DateTimeField(auto_now=True, db_column='_sync_updated')
    _sync_checksum  = models.CharField(max_length=64, blank=True, db_column='_sync_checksum')
    # Checksum dipakai untuk deteksi perubahan di tabel tanpa tanggal_server

    class Meta:
        abstract = True
```

#### 1.2 Contoh Model Tier 1 (`app_master/models.py`)

```python
class Barang(SyncMetaMixin):
    """Tabel: m_barang — Master data barang."""
    kd_barang       = models.CharField(max_length=30, primary_key=True)
    kd_kategori     = models.CharField(max_length=6, blank=True)
    kd_jenis_bahan  = models.CharField(max_length=6, blank=True)
    kd_model        = models.CharField(max_length=6, blank=True)
    kd_merk         = models.CharField(max_length=6, blank=True)
    kd_warna        = models.CharField(max_length=6, blank=True)
    ukuran          = models.FloatField(null=True, blank=True)
    nama            = models.CharField(max_length=50)
    keterangan      = models.CharField(max_length=50, blank=True)
    status          = models.CharField(max_length=1, blank=True)
    status_pinjam   = models.CharField(max_length=1, blank=True)
    pabrik          = models.CharField(max_length=1, blank=True)
    tanggal_daftar  = models.DateTimeField()

    class Meta:
        db_table = 'master_barang'
        indexes = [
            models.Index(fields=['nama']),
            models.Index(fields=['kd_kategori']),
            models.Index(fields=['status']),
        ]


class BarangSatuan(SyncMetaMixin):
    """Tabel: m_barang_satuan — Harga jual per satuan.
    CATATAN: Kolom harga_jual TIDAK di-sync otomatis (dikontrol per-server).
    """
    kd_barang   = models.ForeignKey(Barang, on_delete=models.CASCADE,
                                     db_column='kd_barang', to_field='kd_barang')
    kd_satuan   = models.CharField(max_length=6)
    jumlah      = models.DecimalField(max_digits=15, decimal_places=4)
    harga_jual  = models.DecimalField(max_digits=19, decimal_places=4)
    status      = models.CharField(max_length=1)
    margin      = models.FloatField(null=True, blank=True)

    class Meta:
        db_table = 'master_barang_satuan'
        unique_together = [['kd_barang', 'kd_satuan']]
        # Field harga_jual DIKECUALIKAN dari auto-sync (dikontrol manual)
        EXCLUDE_FROM_AUTO_SYNC = ['harga_jual', 'margin']
```

#### 1.3 Daftar Model yang Perlu Dibuat (per Aplikasi)

**`app_master/models.py`** — Tier 1 & 2:
- `Barang`, `BarangDivisi`, `BarangSatuan`, `BarangDivisiDiskon`
- `BarangPromo`, `BarangPromoDetail`
- `BarangGambar`, `BarangFormula`, `BarangStokAkhir`
- `Kategori`, `Satuan`, `Merk`, `Warna`, `Model`, `JenisBahan`
- `Customer`, `Supplier`, `Ekspedisi`, `Kota`, `Negara`, `Bank`, `Kas`
- `Divisi`, `JenisBayar`, `Jurnal`
- `Pegawai`, `Jabatan`, `JamKerja`, `JenisIzin`
- `Aset`, `AsetKategori`, `Kendaraan`, `Voucher`

**`app_transaksi/models.py`** — Tier 3:
- `Penjualan`, `PenjualanDetail`, `PenjualanRetur`, `PenjualanReturDetail`
- `Pembelian`, `PembelianDetail`, `PembelianRetur`, `PembelianReturDetail`
- `PenjualanOrder`, `PenjualanOrderDetail`
- `PembelianOrder`, `PembelianOrderDetail`
- `MutasiStok`, `MutasiStokDetail`, `MutasiKas`
- `OpnameStok`, `PemakaianBarang`, `PemakaianBarangDetail`
- `PiutangCicilan`, `HutangCicilan`, `BiayaOperasional`, `Pendapatan`
- `Tagihan`, `TagihanDetail`, `SuratBerharga`

---

### Fase 2: Koneksi Dinamis & ETL Core (Minggu 2–3)

**Tujuan:** Logika ekstraksi data dari semua server MSSQL berjalan dengan benar, dengan strategi yang tepat per jenis tabel.

#### 2.1 Connection Manager (`app_sync/connectors.py`)

```python
import pyodbc
from contextlib import contextmanager
from app_core.models import ServerConfig

@contextmanager
def get_mssql_connection(server: ServerConfig):
    """Context manager koneksi MSSQL. Selalu ditutup setelah selesai."""
    conn = pyodbc.connect(server.get_connection_string(), timeout=30)
    try:
        yield conn
    finally:
        conn.close()


def test_server_connection(server: ServerConfig) -> dict:
    """Dipakai oleh tombol 'Test Koneksi' di halaman Kelola Server."""
    try:
        with get_mssql_connection(server) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT @@VERSION")
            version = cursor.fetchone()[0]
        return {'success': True, 'message': version[:80]}
    except Exception as e:
        return {'success': False, 'message': str(e)}
```

#### 2.2 Strategi Sync per Jenis Tabel

```
┌──────────────────────────────────────────────────────────────┐
│           DECISION TREE: Strategi Sync per Tabel             │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  Apakah tabel punya kolom tanggal_server?                   │
│                                                              │
│  YA ──► Gunakan INCREMENTAL SYNC                            │
│         Query: WHERE tanggal_server > {last_sync_time}      │
│         Action: bulk_create (baru) + bulk_update (ada)      │
│         Deteksi: bandingkan dengan PK di database lokal     │
│                                                              │
│  TIDAK ──► Apakah ini tabel master kecil (< 50.000 baris)?  │
│            YA ──► FULL REPLACE                              │
│                   Truncate + bulk_insert ulang              │
│                   (aman untuk m_kategori, m_satuan, dll.)   │
│                                                              │
│            TIDAK ──► CHECKSUM COMPARE                       │
│                      Hash per baris (MD5 field utama)       │
│                      Update hanya baris yang hashnya beda   │
│                      (untuk m_barang, m_customer, dll.)     │
│                                                              │
│  KHUSUS ──► m_barang_satuan.harga_jual                     │
│             TIDAK di-sync otomatis                          │
│             Hanya diupdate via fitur Price Sync Manual      │
└──────────────────────────────────────────────────────────────┘
```

#### 2.3 Implementasi ETL Utama (`app_sync/etl.py`)

```python
import hashlib
import pyodbc
from django.db import transaction
from typing import Type
from django.db.models import Model

CHUNK_SIZE = 5_000   # Baris per batch

def compute_row_checksum(row: dict, key_fields: list) -> str:
    """Checksum MD5 dari nilai field kunci sebuah baris."""
    values = '|'.join(str(row.get(f, '')) for f in key_fields)
    return hashlib.md5(values.encode()).hexdigest()


def sync_incremental(server, table_name: str, model: Type[Model],
                     field_map: dict, pk_field: str,
                     progress_callback=None):
    """
    Sync tabel dengan kolom tanggal_server.
    Hanya menarik data yang lebih baru dari last sync.
    """
    from app_core.models import SyncLog
    last_log = SyncLog.objects.filter(
        server=server, tabel=table_name, status='success'
    ).order_by('-selesai_pada').first()

    last_sync = last_log.selesai_pada if last_log else '2000-01-01'

    with get_mssql_connection(server) as conn:
        cursor = conn.cursor()

        # Ambil total dulu untuk progress
        cursor.execute(
            f"SELECT COUNT(*) FROM {table_name} WHERE tanggal_server > ?",
            [last_sync]
        )
        total = cursor.fetchone()[0]

        offset = 0
        processed = 0
        while True:
            cursor.execute(
                f"""SELECT * FROM {table_name}
                    WHERE tanggal_server > ?
                    ORDER BY tanggal_server
                    OFFSET ? ROWS FETCH NEXT ? ROWS ONLY""",
                [last_sync, offset, CHUNK_SIZE]
            )
            rows = cursor.fetchall()
            if not rows:
                break

            columns = [col[0] for col in cursor.description]
            _upsert_batch(model, rows, columns, field_map, pk_field)

            processed += len(rows)
            offset += CHUNK_SIZE

            if progress_callback:
                progress_callback(processed, total)   # Update Redis progress


def _upsert_batch(model, rows, columns, field_map, pk_field):
    """Pisahkan baris baru & lama, lalu bulk create/update."""
    data = [dict(zip(columns, row)) for row in rows]
    pks = [d[pk_field] for d in data]

    existing_pks = set(
        model.objects.filter(**{f'{pk_field}__in': pks})
        .values_list(pk_field, flat=True)
    )

    to_create, to_update = [], []
    for d in data:
        obj = model(**{field_map.get(k, k): v for k, v in d.items() if k in field_map})
        if d[pk_field] in existing_pks:
            to_update.append(obj)
        else:
            to_create.append(obj)

    with transaction.atomic():
        if to_create:
            model.objects.bulk_create(to_create, ignore_conflicts=True)
        if to_update:
            update_fields = [f for f in field_map.values() if f != pk_field]
            model.objects.bulk_update(to_update, update_fields)
```

#### 2.4 Logika Khusus Gudang sebagai Master (m_barang & m_customer)

Hanya dua tabel ini yang menjadikan Gudang sebagai sumber kebenaran utama. Tabel lain (m_supplier, m_kategori, dll.) di-sync langsung dari masing-masing server tanpa hierarki Gudang.

```python
# Tabel yang menggunakan aturan "Gudang sebagai master"
GUDANG_MASTER_TABLES = {
    'm_barang':   (Barang,   FIELD_MAP_BARANG,   'kd_barang'),
    'm_customer': (Customer, FIELD_MAP_CUSTOMER, 'kd_customer'),
}

def sync_with_gudang_rule(table_name: str, all_servers: list):
    """
    Sync m_barang atau m_customer dengan aturan:
    - Gudang di-sync pertama, hasilnya menjadi referensi canonical di DB lokal.
    - Grosir/Retail di-sync setelahnya:
        * Jika PK sudah ada (dari Gudang) → UPDATE field yang berubah.
        * Jika PK belum ada (barang/customer baru yang hanya ada di server ini)
          → tetap CREATE, dengan _sync_server menunjuk ke server asal.
    """
    model, field_map, pk_field = GUDANG_MASTER_TABLES[table_name]

    # Langkah 1: Sync dari Gudang dulu — jadi anchor record
    gudang_servers = [s for s in all_servers if s.tipe == 'gudang']
    for server in gudang_servers:
        sync_checksum_compare(server, table_name, model, field_map, pk_field)

    # Langkah 2: Sync dari Grosir & Retail
    # Record yang sudah ada dari Gudang hanya di-UPDATE jika checksum berubah.
    # Record yang belum ada di DB lokal → di-CREATE (tidak dibuang).
    other_servers = [s for s in all_servers if s.tipe != 'gudang']
    for server in other_servers:
        sync_checksum_compare(
            server, table_name, model, field_map, pk_field,
            skip_fields_if_exists=['nama', 'status']  # Jangan overwrite field kunci dari Gudang
        )


def sync_checksum_compare(server, table_name, model, field_map, pk_field,
                           skip_fields_if_exists=None, progress_callback=None):
    """
    Sync tabel tanpa tanggal_server menggunakan perbandingan checksum MD5.
    Hanya baris yang checksumnya berbeda yang di-UPDATE.
    """
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

            columns  = [col[0] for col in cursor.description]
            data     = [dict(zip(columns, row)) for row in rows]
            pks      = [d[pk_field] for d in data]

            # Ambil checksum yang tersimpan di DB lokal
            existing = {
                obj[pk_field]: obj['_sync_checksum']
                for obj in model.objects.filter(
                    **{f'{pk_field}__in': pks}
                ).values(pk_field, '_sync_checksum')
            }

            to_create, to_update = [], []
            for d in data:
                new_checksum = compute_row_checksum(d, list(field_map.keys()))
                mapped = {field_map.get(k, k): v for k, v in d.items() if k in field_map}
                mapped['_sync_checksum'] = new_checksum
                mapped['_sync_server_id'] = server.pk

                pk_val = d[pk_field]
                if pk_val not in existing:
                    to_create.append(model(**mapped))
                elif existing[pk_val] != new_checksum:
                    if skip_fields_if_exists:
                        for f in skip_fields_if_exists:
                            mapped.pop(f, None)
                    to_update.append(model(**mapped))
                # else: checksum sama → skip

            with transaction.atomic():
                if to_create:
                    model.objects.bulk_create(to_create, ignore_conflicts=True)
                if to_update:
                    update_fields = [f for f in mapped if f != pk_field]
                    model.objects.bulk_update(to_update, update_fields)

            processed += len(rows)
            offset    += CHUNK_SIZE
            if progress_callback:
                progress_callback(processed, total)
```

---

### Fase 3: Celery Tasks & Real-time Progress (Minggu 3–4)

**Tujuan:** Semua proses berat berjalan di background. Web bisa memantau progress secara real-time.

#### 3.1 Struktur Task (`app_sync/tasks.py`)

```python
from celery import shared_task, current_task
from django.utils import timezone
from app_core.models import SyncLog, ServerConfig

def _update_progress(log: SyncLog, current: int, total: int, message: str = ''):
    """Update progress di DB dan Redis untuk polling frontend."""
    pct = round((current / total * 100) if total > 0 else 0, 1)
    SyncLog.objects.filter(pk=log.pk).update(
        progress_pct=pct,
        data_baru=current,
        total_data=total,
    )
    # Update Celery task state agar bisa dipoll via /task-status/<task_id>/
    current_task.update_state(
        state='PROGRESS',
        meta={'current': current, 'total': total, 'pct': pct, 'message': message}
    )


@shared_task(bind=True, name='sync.full_sync')
def task_full_sync(self, server_id: int):
    """Full Sync: Tarik semua data dari satu server MSSQL."""
    server = ServerConfig.objects.get(pk=server_id)
    log = SyncLog.objects.create(
        server=server, jenis='full_sync', celery_task_id=self.request.id
    )
    try:
        # Urutan sync: master dulu, baru transaksi
        SYNC_ORDER = [
            ('m_kategori',   Kategori,   FIELD_MAP_KATEGORI,   'kd_kategori'),
            ('m_satuan',     Satuan,     FIELD_MAP_SATUAN,     'kd_satuan'),
            ('m_merk',       Merk,       FIELD_MAP_MERK,       'kd_merk'),
            ('m_barang',     Barang,     FIELD_MAP_BARANG,     'kd_barang'),
            ('m_customer',   Customer,   FIELD_MAP_CUSTOMER,   'kd_customer'),
            # ... dst
        ]
        for tbl, model, fmap, pk in SYNC_ORDER:
            sync_incremental(server, tbl, model, fmap, pk,
                             progress_callback=lambda c, t: _update_progress(log, c, t, tbl))

        log.status = 'success'
        log.selesai_pada = timezone.now()
        log.save()

    except Exception as e:
        log.status = 'failed'
        log.pesan_error = str(e)
        log.selesai_pada = timezone.now()
        log.save()
        raise


@shared_task(bind=True, name='sync.auto_sync')
def task_auto_sync(self, server_id: int):
    """Auto Sync: Hanya tabel dengan tanggal_server, incremental."""
    # Mirip full_sync tapi hanya tabel Tier 3 (transaksi)
    ...


@shared_task(bind=True, name='sync.monthly_check')
def task_monthly_check(self, server_id: int):
    """Cek & rekonsiliasi data 1 bulan terakhir."""
    ...


@shared_task(bind=True, name='sync.yearly_check')
def task_yearly_check(self, server_id: int):
    """Cek & rekonsiliasi data 1 tahun terakhir."""
    ...


@shared_task(bind=True, name='sync.full_check')
def task_full_check(self, server_id: int):
    """Full Check: Bandingkan seluruh data. Bisa berjam-jam."""
    ...


@shared_task(bind=True, name='sync.price_sync')
def task_price_sync(self, server_id: int, barang_list: list):
    """Sync harga terpilih dari server tertentu ke DB lokal."""
    # barang_list = [{'kd_barang': '...', 'kd_satuan': '...'}, ...]
    ...
```

#### 3.2 Real-time Progress via Polling

Untuk simplicity, gunakan **AJAX polling** (bukan WebSocket). Frontend memanggil endpoint setiap 2 detik:

```
GET /api/task-status/<task_id>/
→ Response: {state, current, total, pct, message, status}
```

```python
# app_sync/views.py
from celery.result import AsyncResult

def task_status_view(request, task_id):
    result = AsyncResult(task_id)
    if result.state == 'PROGRESS':
        data = result.info   # {'current', 'total', 'pct', 'message'}
    elif result.state == 'SUCCESS':
        data = {'pct': 100, 'status': 'done'}
    elif result.state == 'FAILURE':
        data = {'pct': 0, 'status': 'error', 'message': str(result.info)}
    else:
        data = {'pct': 0, 'status': result.state}
    return JsonResponse(data)
```

#### 3.3 Jadwal Auto Sync (Celery Beat)

Dikonfigurasi via web (halaman Kelola Server → tab Jadwal), disimpan di tabel `django_celery_beat_periodictask`:

| Task | Default Jadwal | Bisa Diubah via Web |
|---|---|---|
| Auto Sync (semua server) | Setiap 15 menit | ✅ |
| Monthly Check | Setiap tgl 1 jam 01:00 | ✅ |
| Yearly Check | Setiap 1 Jan jam 02:00 | ✅ |

---

### Fase 4: Web Control Panel (Minggu 4–5)

**Tujuan:** Semua operasi bisa dilakukan tanpa terminal.

#### 4.1 Peta Halaman Web

```
/                           → Dashboard
/login/                     → Login
/logout/                    → Logout

/server/                    → Daftar server MSSQL
/server/tambah/             → Form tambah server + Test Koneksi
/server/<id>/edit/          → Edit server
/server/<id>/hapus/         → Hapus server (konfirmasi)

/user/                      → Daftar user sistem
/user/tambah/               → Form tambah user
/user/<id>/edit/            → Edit user & reset password

/sync/                      → Pusat Kontrol Sync (tombol-tombol aksi)
/sync/log/                  → Riwayat semua sync + filter
/sync/log/<id>/             → Detail log: baris per baris error, progress, dll.
/sync/log/<id>/retry/       → Tombol "Coba Lagi" untuk log yang gagal

/master/barang/             → Tabel m_barang (read-only, searchable, paginasi)
/master/barang/<kd>/        → Detail satu barang + harga per server
/master/kategori/           → Tabel m_kategori
/master/customer/           → Tabel m_customer
/master/supplier/           → Tabel m_supplier

/harga/                     → Halaman Sync Harga Manual
/harga/perbandingan/        → Tabel perbandingan harga antar server
/harga/sync/                → POST endpoint untuk eksekusi price sync

/api/task-status/<task_id>/ → Polling progress Celery task (JSON)
/api/server/<id>/test/      → Test koneksi server (JSON)
```

#### 4.2 Dashboard (`/`)

```
┌───────────────────────────────────────────────────────────┐
│  GrosirPusat Sync  [User: admin ▼]            [Logout]    │
├───────────────────────────────────────────────────────────┤
│                                                           │
│  Status Koneksi Server:                                   │
│  ● Gudang-01    [●Aktif]  Last sync: 5 mnt lalu  ✓ OK   │
│  ● Grosir-01   [●Aktif]  Last sync: 5 mnt lalu  ✓ OK   │
│  ● Retail-01   [●Aktif]  Last sync: 8 mnt lalu  ✓ OK   │
│                                                           │
│  ┌────────────┐  ┌────────────┐  ┌────────────────────┐  │
│  │ Total Brg  │  │ Total Cust │  │  Transaksi 30hr    │  │
│  │  12,450    │  │   3,210    │  │      45,890        │  │
│  └────────────┘  └────────────┘  └────────────────────┘  │
│                                                           │
│  Log Sync Terbaru:                                        │
│  ✓ Auto Sync Gudang-01    14:45  200 baris  [OK]         │
│  ✓ Auto Sync Grosir-01    14:45  134 baris  [OK]         │
│  ✗ Auto Sync Retail-01    14:30  Error!     [Retry]      │
│                                                           │
│  [ Jalankan Full Sync ▼ ]  [ Jalankan Check ▼ ]          │
└───────────────────────────────────────────────────────────┘
```

#### 4.3 Halaman Pusat Kontrol Sync (`/sync/`)

Tombol-tombol aksi akan:
1. Menampilkan konfirmasi (modal)
2. Memanggil endpoint POST yang memulai Celery task
3. Redirect ke halaman progress polling

```
┌─────────────────────────────────────────────────────┐
│  Pusat Kontrol Sinkronisasi                         │
├─────────────────────────────────────────────────────┤
│  Pilih Server: [Gudang-01 ▼]                        │
│                                                     │
│  SYNC DATA                                          │
│  ┌──────────────┐  ┌──────────────┐               │
│  │  Full Sync   │  │  Auto Sync   │               │
│  │ (Semua data) │  │ (Data baru)  │               │
│  └──────────────┘  └──────────────┘               │
│                                                     │
│  CEK & REKONSILIASI                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────┐  │
│  │Monthly Check │  │ Yearly Check │  │Full Check│  │
│  │  (30 hari)   │  │  (1 tahun)   │  │ (Semua)  │  │
│  └──────────────┘  └──────────────┘  └──────────┘  │
│                                                     │
│  [Lihat Riwayat Log →]                              │
└─────────────────────────────────────────────────────┘
```

**Saat tombol diklik → Progress bar muncul:**
```
┌─────────────────────────────────────────────────────┐
│  Full Sync Gudang-01 sedang berjalan...             │
│                                                     │
│  ████████████░░░░░░░░░░░░  45%                     │
│  m_barang: 5.620 / 12.450 baris                    │
│  Estimasi selesai: ~3 menit                         │
│                                                     │
│  [ Lihat Log Detail ]                               │
└─────────────────────────────────────────────────────┘
```

#### 4.4 Halaman Sync Harga Manual (`/harga/`)

```
┌────────────────────────────────────────────────────────────────────┐
│  Sync Harga Manual                                                 │
│                                                                    │
│  Sumber Harga: [Grosir-01 ▼]   Filter: [cari nama barang...]     │
│                                                                    │
│  □ | Kode Barang  | Nama         | Harga Lokal | Harga Server |   │
│  ──────────────────────────────────────────────────────────────   │
│  ☑ | BRG-001      | Kemeja Putih | Rp 85.000   | Rp 80.000   |  │
│  □ | BRG-002      | Celana Jeans | Rp 150.000  | Rp 145.000  |  │
│  ☑ | BRG-003      | Kaos Polos   | Rp 45.000   | Rp 42.000   |  │
│  ...                                                               │
│                                                                    │
│  2 barang dipilih                                                  │
│  [ ☑ Pilih Semua ]    [ Sync Harga Terpilih (2) ]                 │
└────────────────────────────────────────────────────────────────────┘
```

#### 4.5 Halaman Log Error (`/sync/log/`)

```
┌────────────────────────────────────────────────────────────────────┐
│  Riwayat Sinkronisasi                     Filter: [Semua ▼]       │
│                                                                    │
│  Waktu           | Server     | Jenis       | Status | Aksi       │
│  ──────────────────────────────────────────────────────────────   │
│  16/06 14:45     | Gudang-01  | Auto Sync   | ✓ OK   | [Detail]  │
│  16/06 14:30     | Retail-01  | Auto Sync   | ✗ GAGAL| [Detail]  │
│                                                                    │
│  ─── Detail Log #2 (Retail-01, GAGAL): ───                        │
│  Error: [08001] Connection timeout after 30s                       │
│  Tabel terakhir: t_penjualan (offset 15.000)                      │
│  Data berhasil: 15.000 baris                                       │
│                                                                    │
│  [ 🔄 Coba Lagi dari Titik Terakhir ]                              │
└────────────────────────────────────────────────────────────────────┘
```

---

### Fase 5: Rekonsiliasi Data (Minggu 5)

**Tujuan:** Tiga jenis pencocokan data berjalan dengan akurat.

#### 5.1 Strategi per Jenis Check

```python
# app_sync/reconciliation.py

def check_monthly(server, months=1):
    """
    Cek data N bulan terakhir.
    Strategi: Bandingkan COUNT dan checksum per tanggal di server vs lokal.
    """
    from datetime import datetime, timedelta
    cutoff = datetime.now() - timedelta(days=30 * months)

    TABLES_TO_CHECK = [
        ('t_penjualan',  Penjualan,  'tanggal', 'no_transaksi'),
        ('t_pembelian',  Pembelian,  'tanggal', 'no_transaksi'),
        # ... semua tabel Tier 3
    ]

    discrepancies = []
    with get_mssql_connection(server) as conn:
        for tbl, model, date_col, pk_col in TABLES_TO_CHECK:
            # 1. Ambil PK dari server untuk periode ini
            cursor = conn.cursor()
            cursor.execute(
                f"SELECT {pk_col} FROM {tbl} WHERE {date_col} >= ?", [cutoff]
            )
            server_pks = set(r[0] for r in cursor.fetchall())

            # 2. Ambil PK dari lokal untuk periode sama
            local_pks = set(
                model.objects.filter(
                    **{f'{date_col}__gte': cutoff},
                    _sync_server=server
                ).values_list(pk_col, flat=True)
            )

            # 3. Cari yang selip
            missing = server_pks - local_pks
            extra   = local_pks - server_pks
            if missing or extra:
                discrepancies.append({
                    'table': tbl, 'missing': list(missing)[:100],
                    'extra': list(extra)[:100]
                })

    return discrepancies   # Disimpan ke SyncLog untuk ditampilkan di web


def check_yearly(server):
    return check_monthly(server, months=12)


def check_full(server):
    """Full check: bandingkan semua data. Proses sangat lama."""
    # Sama seperti check_monthly tapi tanpa filter tanggal
    # Gunakan hash per 10.000 baris untuk efisiensi
    ...
```

---

### Fase 6: Testing & Deployment (Minggu 6)

#### 6.1 Indexing PostgreSQL yang Wajib Ada

```sql
-- m_barang — kolom yang sering difilter
CREATE INDEX idx_barang_nama       ON master_barang (nama);
CREATE INDEX idx_barang_kategori   ON master_barang (kd_kategori);
CREATE INDEX idx_barang_status     ON master_barang (status);

-- Tabel transaksi — kolom untuk incremental sync & query laporan
CREATE INDEX idx_penjualan_tanggal        ON transaksi_penjualan (tanggal);
CREATE INDEX idx_penjualan_server_time    ON transaksi_penjualan (_sync_updated);
CREATE INDEX idx_penjualan_customer       ON transaksi_penjualan (kd_customer);
CREATE INDEX idx_pembelian_tanggal        ON transaksi_pembelian (tanggal);
CREATE INDEX idx_pembelian_supplier       ON transaksi_pembelian (kd_supplier);

-- SyncLog — untuk filter di halaman monitoring
CREATE INDEX idx_synclog_server   ON core_synclog (server_id, mulai_pada);
CREATE INDEX idx_synclog_status   ON core_synclog (status, mulai_pada);
```

#### 6.2 Stack Deployment

```
Server Production:
├── Nginx               → Reverse proxy, serve static files
├── Gunicorn            → WSGI server Django (4-8 workers)
├── Celery Worker       → Background task processor
│   └── Concurrency: 4  (sesuaikan dengan RAM server)
├── Celery Beat         → Penjadwal periodik (1 instance saja!)
└── Redis               → Message broker + progress state

Systemd services (auto-restart jika crash):
├── grosirpusat-web.service      → Gunicorn
├── grosirpusat-worker.service   → Celery Worker
└── grosirpusat-beat.service     → Celery Beat
```

**`/etc/systemd/system/grosirpusat-worker.service`:**
```ini
[Unit]
Description=GrosirPusat Celery Worker
After=network.target redis.service

[Service]
WorkingDirectory=/opt/grosirpusat_sync
ExecStart=/opt/grosirpusat_sync/venv/bin/celery -A grosirpusat_sync worker
    --loglevel=INFO --concurrency=4 --max-tasks-per-child=100
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

#### 6.3 Stress Testing Checklist

```
□ Full Sync dengan 1 juta baris t_penjualan → pantau RAM Celery
□ Auto Sync berjalan bersamaan dari 3 server berbeda → cek race condition
□ Simulasi koneksi MSSQL putus di tengah sync → verifikasi retry & log error
□ Full Check dengan 5 juta baris → ukur durasi & CPU usage
□ 5 user web buka halaman monitoring bersamaan → pastikan polling tidak overload
□ CHUNK_SIZE disesuaikan: mulai 5.000, naik bertahap hingga RAM aman
```

---

## Ringkasan Deliverable per Minggu

| Minggu | Deliverable |
|---|---|
| **1** | Proyek Django jalan, login, dashboard kosong, CRUD Server, CRUD User |
| **1–2** | Semua model Django + migrasi PostgreSQL, tampil data m_barang & m_kategori |
| **2–3** | ETL core berjalan manual via `manage.py shell`, logika barang Gudang |
| **3–4** | Celery terintegrasi, progress realtime via polling, jadwal auto sync |
| **4–5** | Semua halaman web: monitoring, log error, price sync UI, retry button |
| **5** | Fitur Monthly/Yearly/Full Check selesai dan bisa dipicu dari web |
| **6** | Deployment ke production, indexing, stress test, dokumentasi singkat |

---

## Catatan Teknis Penting

### Masalah Umum & Solusinya

| Masalah | Solusi |
|---|---|
| Koneksi MSSQL timeout saat Full Sync | Set `timeout=0` di pyodbc untuk query panjang, atau gunakan cursor dengan `fetchmany()` |
| `kd_barang` berbeda format antar server | Normalisasi ke strip + upper sebelum bandingkan |
| Celery beat menjadwalkan task duplikat | Gunakan satu instance Beat saja, lock via Redis jika perlu |
| Django Admin lambat untuk tabel besar | Gunakan `list_select_related = False` dan custom QuerySet dengan `defer()` |
| Password server tersimpan plaintext | Enkripsi wajib dengan `cryptography.fernet` sebelum masuk DB |
| Harga terbalik saat retry price sync | Simpan "snapshot before" di SyncLog sebelum overwrite harga |

### Kolom `kd_customer` Perlu Perhatian
Berbeda dari tabel lain yang pakai `JR_KODE_MASTER` (6 char), `m_customer.kd_customer` adalah `varchar(20)`. Pastikan field Django dan filter query mengakomodasi panjang ini.

### Kolom Nullable di Tabel Transaksi
Banyak kolom `tanggal_server` di tabel transaksi ditandai nullable (`1` di kolom nullable file schema). Artinya ada kemungkinan record lama tidak punya nilai `tanggal_server`. Tangani ini di query incremental sync:
```sql
WHERE tanggal_server > ? OR (tanggal_server IS NULL AND tanggal > ?)
```
