import re

models_file = r'd:\Project\DjangoPOS\app_transaksi\models.py'
with open(models_file, 'r') as f:
    content = f.read()

classes = re.findall(r'class (\w+)\(SyncMetaMixin\):\n((?:    .*\n)+)', content)

models_info = {}
for class_name, body in classes:
    table_match = re.search(r"db_table = '(.+?)'", body)
    table_name = table_match.group(1) if table_match else None
    
    pk_match = re.search(r"(\w+) = models\.\w+Field\(.*primary_key=True", body)
    pk_field = pk_match.group(1) if pk_match else None
    
    fields = re.findall(r'    (\w+) = models\.', body)
    
    date_field = None
    if 'tanggal' in fields:
        date_field = 'tanggal'
    elif 'tanggal_server' in fields:
        date_field = 'tanggal_server'
    elif 'awal' in fields:
        date_field = 'awal'
    elif 'masuk' in fields:
        date_field = 'masuk'
        
    fk_field = 'no_transaksi'
    if 'no_nota' in fields:
        fk_field = 'no_nota'
    if 'no_retur' in fields:
        fk_field = 'no_retur'
    if 'no_order' in fields:
        fk_field = 'no_order'
        
    models_info[class_name] = {
        'table': table_name,
        'pk': pk_field,
        'date': date_field,
        'fk': fk_field,
        'is_detail': 'Detail' in class_name or date_field is None
    }

print("SYNC_ORDER = [")
for name, info in models_info.items():
    if not info['is_detail']:
        # Find detail tables
        details = []
        for d_name, d_info in models_info.items():
            if d_info['is_detail'] and (d_name.startswith(name + 'Detail') or d_name == name + 'Pegawai'):
                details.append(f"('{d_info['table']}', {d_name}, '{d_info['fk']}')")
                
        details_str = "[" + ", ".join(details) + "]"
        print(f"    ('{info['table']}', {name}, '{info['pk']}', '{info['date']}', {details_str}),")
print("]")
