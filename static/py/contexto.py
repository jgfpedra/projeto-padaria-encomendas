# static/py/context_processors.py
import psycopg2
from static.py.config.db import get_db_connection
from static.py.config.db_vr import get_db_vr
from static.py.login_required import login_required
from flask import session

def inject_user():
    id_operador = session.get('id_operador')
    usuario = {
        'loja': None,
        'nome': "Usuário não encontrado"
    }

    if id_operador:
        conn = get_db_connection()  # Get the connection to the main DB
        try:
            with conn.cursor() as cursor:
                # Fetch user info
                cursor.execute("SELECT nome, id_loja FROM operador WHERE id = %s", (id_operador,))
                user_info = cursor.fetchone()  # Get user info

            if user_info:  # Check if user_info is not None
                conn_vr = get_db_vr()  # Get the connection for the VR database
                try:
                    with conn_vr.cursor() as cursor:
                        # Fetch store info
                        cursor.execute("SELECT descricao FROM loja WHERE id = %s", (user_info[1],))
                        loja_info = cursor.fetchone()  # Get store info
                finally:
                    conn_vr.close()  # Ensure the VR connection is closed

                # Prepare user information
                usuario['loja'] = loja_info[0] if loja_info else None
                usuario['nome'] = user_info[0] if user_info else "Usuário não encontrado"

        finally:
            conn.close()  # Ensure the main DB connection is closed

    return dict(usuario=usuario)
