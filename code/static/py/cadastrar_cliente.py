# static/py/cliente.py
from db import get_db_connection

def create_table():
    """Create the cliente table if it does not exist."""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS cliente (
            id SERIAL PRIMARY KEY,
            nome VARCHAR(100) NOT NULL,
            endereco VARCHAR(200) NOT NULL,
            numero VARCHAR(50) NOT NULL,
            bairro VARCHAR(100) NOT NULL,
            complemento VARCHAR(100),
            municipio VARCHAR(100) NOT NULL,
            observacao TEXT,
            telefones TEXT
        )
    ''')
    conn.commit()
    cur.close()
    conn.close()

def insert_cliente(nome, endereco, numero, bairro, complemento, municipio, observacao, telefones):
    """Insert a new cliente into the database."""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('''
        INSERT INTO cliente (nome, endereco, numero, bairro, complemento, municipio, observacao, telefones)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    ''', (nome, endereco, numero, bairro, complemento, municipio, observacao, telefones))
    conn.commit()
    cur.close()
    conn.close()

def get_next_codigo():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT COALESCE(MAX(id), 0) + 1 FROM cliente')
    next_codigo = cur.fetchone()[0]
    cur.close()
    conn.close()
    return next_codigo
