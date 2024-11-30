from flask import Flask, render_template, request, Blueprint, flash, redirect, url_for, jsonify
import psycopg2
from static.py.config.db import get_db_connection
from static.py.login_required import login_required

cliente_cadastrar_bp = Blueprint('cliente_cadastrar_bp', __name__)

@cliente_cadastrar_bp.route('/cliente_cadastrar', methods=['GET', 'POST'])
@cliente_cadastrar_bp.route('/cliente_cadastrar/<int:id>', methods=['GET', 'POST'])
@login_required
def cliente_cadastrar(id=None):
    if request.method == 'POST':
        # Retrieve form data
        id = request.form.get('id', '')
        nome = request.form.get('nome', '')
        endereco = request.form.get('endereco', '')
        numero = request.form.get('numero', '')
        bairro = request.form.get('bairro', '')
        complemento = request.form.get('complemento', '')
        observacao = request.form.get('observacao', '')
        telefones = request.form.getlist('telefones')  # This will be a list of phone numbers

        conn = get_db_connection()
        cur = conn.cursor()

        try:
            cur.execute('SELECT id FROM cliente WHERE id = %s', (id,))
            existing_client = cur.fetchone()

            if existing_client:
                # Update the existing cliente
                cur.execute('''
                    UPDATE cliente
                    SET nome = %s, endereco = %s, numero = %s, bairro = %s, complemento = %s, observacao = %s
                    WHERE id = %s
                ''', (nome, endereco, numero, bairro, complemento, observacao, id))

                # Delete old phone numbers
                cur.execute('DELETE FROM telefone WHERE cliente_id = %s', (id,))

                # Handle telefones (single or multiple)
                telefone_list = []
                if isinstance(telefones, list) and telefones:  # If it's a list of phone numbers
                    telefone_list = [telefone.strip() for telefone in telefones if telefone.strip()]
                elif isinstance(telefones, str) and telefones:  # If it's a single phone number (comma-separated)
                    telefone_list = [telefone.strip() for telefone in telefones.split(',') if telefone.strip()]

                # Insert new telefones
                for telefone in telefone_list:
                    if telefone:  # Only add non-empty telefone entries
                        # Check if the telefone already exists for the given cliente_id
                        cur.execute('SELECT COUNT(*) FROM telefone WHERE telefone = %s', (telefone,))
                        exists = cur.fetchone()[0] > 0
                        if exists:
                            return jsonify(success=False, message=f'O telefone {telefone} já está cadastrado.'), 400
                        cur.execute('''
                            INSERT INTO telefone (cliente_id, telefone)
                            VALUES (%s, %s)
                        ''', (id, telefone))

                conn.commit()  # Commit the changes
                return jsonify(success=True, message='Cliente e telefones atualizados com sucesso')
            else:
                # If the ID does not exist, insert a new record
                insert_cliente(nome, endereco, numero, bairro, complemento, observacao, telefones)
                conn.commit()
                return jsonify(success=True, message='Cliente cadastrado com sucesso')
        except Exception as e:
            conn.rollback()
            return jsonify(success=False, message=str(e)), 500
        finally:
            cur.close()
            conn.close()

    cliente = None
    telefones_list = []

    if id:
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute('SELECT * FROM cliente WHERE id = %s', (id,))
        cliente = cur.fetchone()

        if cliente:
            cur.execute('SELECT telefone FROM telefone WHERE cliente_id = %s', (id,))
            telefones = cur.fetchall()
            telefones_list = [telefone[0] for telefone in telefones]  # Extract telefone values into a list

        cur.close()
        conn.close()

    cliente_data = {
        'id': cliente[0] if cliente else '',
        'nome': cliente[1] if cliente else '',
        'endereco': cliente[2] if cliente else '',
        'numero': cliente[3] if cliente else '',
        'bairro': cliente[4] if cliente else '',
        'complemento': cliente[5] if cliente else '',
        'observacao': cliente[6] if cliente else '',
        'telefones': telefones_list  # Use the telefones_list for rendering
    }

    next_codigo = get_next_codigo() if cliente is None else cliente[0]
    return render_template('cliente_cadastrar.html', cliente=cliente_data, next_codigo=next_codigo)

def get_next_codigo():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT COALESCE(MAX(id), 0) + 1 FROM cliente')
    next_codigo = cur.fetchone()[0]
    cur.close()
    conn.close()
    return next_codigo

def insert_cliente(nome, endereco, numero, bairro, complemento, observacao, telefones):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('''
        INSERT INTO cliente (nome, endereco, numero, bairro, complemento, observacao)
        VALUES (%s, %s, %s, %s, %s, %s)
        RETURNING id;
    ''', (nome, endereco, numero, bairro, complemento, observacao))
    cliente_id = cur.fetchone()[0]  # Get the new cliente id


    # Ensure telefones is always a list, even if there's only one phone number
    telefones = telefones.strip()

    # If the input contains multiple phone numbers (comma-separated), split it
    if ',' in telefones:
        telefone_list = telefones.split(',')
    else:
        # If it's just one telefone, put it in a list to process
        telefone_list = [telefones]

    # Loop through all phone numbers (single or multiple)
    for telefone in telefone_list:
        telefone = telefone.strip()  # Clean up any whitespace

        if telefone:  # Only insert if the telefone is not empty
            # Check if the telefone already exists for the given cliente_id
            cur.execute('SELECT COUNT(*) FROM telefone WHERE cliente_id = %s AND telefone = %s', (cliente_id, telefone))
            exists = cur.fetchone()[0] > 0

            if not exists:
                cur.execute('''
                    INSERT INTO telefone (cliente_id, telefone)
                    VALUES (%s, %s)
                ''', (cliente_id, telefone))

    conn.commit()
    cur.close()
    conn.close()
