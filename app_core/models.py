from django.db import models
from cryptography.fernet import Fernet
from django.conf import settings

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
        pwd_data = self.password
        if isinstance(pwd_data, memoryview):
            pwd_data = bytes(pwd_data)
            
        try:
            pwd = Fernet(settings.SECRET_KEY_BYTES).decrypt(pwd_data).decode()
        except Exception:
            pwd = ""
            
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
    details         = models.JSONField(default=dict, blank=True)
    mulai_pada      = models.DateTimeField(auto_now_add=True)
    selesai_pada    = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-mulai_pada']
