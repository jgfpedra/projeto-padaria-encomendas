# static/py/db_vr.py
import psycopg2

# Database connection configuration
DB_CONFIG = {
    'dbname': 'vr_bkp',
    'user': 'postgres',
    'password': 'VrPost@Server',
    'host': '192.168.1.187'
}

def get_db_vr():
    """Establish a connection to the database."""
    conn = psycopg2.connect(**DB_CONFIG)
    return conn
