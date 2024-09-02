# static/py/produtos.py
from db import get_db_connection

def create_table():
    """Create the cliente table if it does not exist."""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS cliente (
            id SERIAL PRIMARY KEY,
            codigo VARCHAR(50) NOT NULL,
            nome VARCHAR(100) NOT NULL,
            endereco VARCHAR(200) NOT NULL,
            numero VARCHAR(50) NOT NULL,
            bairro VARCHAR(100) NOT NULL,
            complemento VARCHAR(100),
            regiao VARCHAR(100) NOT NULL,
            municipio VARCHAR(100) NOT NULL,
            observacao TEXT,
            telefones TEXT
        )
    ''')
    conn.commit()
    cur.close()
    conn.close()

def insert_cliente(codigo, nome, endereco, numero, bairro, complemento, regiao, municipio, observacao, telefones):
    """Insert a new cliente into the database."""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('''
        INSERT INTO cliente (codigo, nome, endereco, numero, bairro, complemento, regiao, municipio, observacao, telefones)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    ''', (codigo, nome, endereco, numero, bairro, complemento, regiao, municipio, observacao, telefones))
    conn.commit()
    cur.close()
    conn.close()
