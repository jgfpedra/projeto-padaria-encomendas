# static/py/config/db.py
import psycopg2

# Database connection configuration
DB_CONFIG = {
    'dbname': 'delivery_db',
    'user': 'postgres',
    'password': 'VrPost@Server',
    'host': 'localhost',  # Ensure this is correct
    'port': 5432,         # Default PostgreSQL port
}

def get_db_connection():
    """Establish a connection to the database."""
    conn = psycopg2.connect(**DB_CONFIG)
    return conn
