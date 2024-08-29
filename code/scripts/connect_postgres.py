import psycopg2
from psycopg2 import sql

# Database connection parameters
host = '192.168.1.178'  # IP address of your Windows machine
port = 5432                    # Default PostgreSQL port
dbname = 'vr_bkp'     # Your database name
user = 'postgres'            # Your PostgreSQL username
password = 'VrPost@Server'        # Your PostgreSQL password

try:
    # Establish the connection
    connection = psycopg2.connect(
        host=host,
        port=port,
        dbname=dbname,
        user=user,
        password=password
    )
    
    # Create a cursor object
    cursor = connection.cursor()

    # Execute a query
    cursor.execute("SELECT version();")

    # Fetch and print the result
    db_version = cursor.fetchone()
    print(f"Database version: {db_version}")

except Exception as error:
    print(f"Error connecting to PostgreSQL database: {error}")

finally:
    # Close the cursor and connection
    if cursor:
        cursor.close()
    if connection:
        connection.close()
