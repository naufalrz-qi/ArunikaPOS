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
