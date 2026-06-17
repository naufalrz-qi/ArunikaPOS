import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'grosirpusat_sync.settings')
django.setup()

from app_transaksi import models

for name in dir(models):
    obj = getattr(models, name)
    if isinstance(obj, type) and issubclass(obj, django.db.models.Model) and obj.__module__ == 'app_transaksi.models':
        # Get fields
        fields = [f.name for f in obj._meta.fields]
        pk_field = obj._meta.pk.name
        table = obj._meta.db_table
        
        # Determine date field
        date_field = None
        if 'tanggal' in fields:
            date_field = 'tanggal'
        elif 'tanggal_server' in fields:
            date_field = 'tanggal_server'
        elif 'masuk' in fields: # For Absensi
            date_field = 'masuk'
            
        print(f"('{table}', {name}, '{pk_field}', '{date_field}'),")
