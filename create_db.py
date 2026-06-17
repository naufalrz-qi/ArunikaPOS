import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

def create_db():
    users_to_try = ['postgres', 'postgre']
    for user in users_to_try:
        try:
            conn = psycopg2.connect(
                dbname='postgres',
                user=user,
                password='12qwaszx#DB',
                host='localhost',
                port='5432'
            )
            conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            cursor = conn.cursor()
            cursor.execute('CREATE DATABASE grosirpusat_local')
            print(f"Database created successfully using user '{user}'")
            return user
        except psycopg2.errors.DuplicateDatabase:
            print(f"Database grosirpusat_local already exists. Connected with '{user}'")
            return user
        except Exception as e:
            print(f"Failed with user '{user}': {e}")
            
    print("Could not connect to PostgreSQL to create the database.")
    return None

if __name__ == '__main__':
    created_user = create_db()
    if created_user and created_user != 'postgres':
        print(f"PLEASE_UPDATE_SETTINGS_USER:{created_user}")
