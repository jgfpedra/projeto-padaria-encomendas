# static/py/cliente.py
from flask import Flask, render_template, request, Blueprint, flash, redirect, url_for
import psycopg2
from static.py.config.db import get_db_connection
from static.py.login_required import login_required
import regex as re

cliente_cadastrar_bp = Blueprint('cliente_cadastrar_bp', __name__)

@cliente_cadastrar_bp.route('/cliente_cadastrar', methods=['GET', 'POST'])
@cliente_cadastrar_bp.route('/cliente_cadastrar/<int:id>', methods=['GET', 'POST'])
@login_required
def cliente_cadastrar(id=None):
    if request.method == 'POST':
        id = request.form.get('id', id)
        nome = request.form.get('nome', '')
        endereco = request.form.get('endereco', '')
        numero = request.form.get('numero', '')
        bairro = request.form.get('bairro', '')
        complemento = request.form.get('complemento', '')
        municipio = request.form.get('municipio', '')
        observacao = request.form.get('observacao', '')
        telefones = ','.join(request.form.getlist('telefones'))

        if not (re.validate_id(id) and re.validate_name(nome) and re.validate_address(endereco) and
            re.validate_number(numero) and re.validate_bairro(bairro) and
            re.validate_complement(complemento) and re.validate_municipio(municipio) and
            re.validate_observacao(observacao) and re.validate_telefones(telefones)):
            flash('Invalid input detected. Please check your inputs and try again.', 'error')

        conn = get_db_connection()
        cur = conn.cursor()

        if id:  # If id is provided, check if it exists and then update or insert
            cur.execute('SELECT id FROM cliente WHERE id = %s', (id,))
            existing_client = cur.fetchone()
            if existing_client:
                # Update the existing record in cliente
                cur.execute('''
                    UPDATE cliente
                    SET nome = %s, endereco = %s, numero = %s, bairro = %s, complemento = %s, municipio = %s, observacao = %s
                    WHERE id = %s
                ''', (nome, endereco, numero, bairro, complemento, municipio, observacao, id))
                
                # Now update the telefones
                telefones = request.form.getlist('telefones')
                
                # First, delete existing telefones for this cliente
                cur.execute('DELETE FROM telefone WHERE cliente_id = %s', (id,))
                
                # Then, insert the new telefones
                for telefone in telefones:
                    if telefone:  # Only add non-empty telefone entries
                        cur.execute('''
                            INSERT INTO telefone (cliente_id, telefone)
                            VALUES (%s, %s)
                        ''', (id, telefone))
                
                flash('Cliente e telefones atualizados com sucesso', 'success')
            else:
                # Insert a new record if the ID does not exist
                insert_cliente(nome, endereco, numero, bairro, complemento, municipio, observacao, telefones)
                flash('Cliente cadastrado com sucesso', 'success')
        else:  # If no id is provided, create a new record
            insert_cliente(nome, endereco, numero, bairro, complemento, municipio, observacao, telefones)
            flash('Cliente cadastrado com sucesso', 'success')

        conn.commit()
        cur.close()
        conn.close()

        return redirect(url_for('pesquisar_cliente_bp.pesquisar_cliente'))

    # GET request: show the form
    cliente = None
    if id:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('SELECT * FROM cliente WHERE id = %s', (id,))
        cliente = cur.fetchone()

        # Fetch telefones for the cliente
        cur.execute('SELECT telefone FROM telefone WHERE cliente_id = %s', (id,))
        telefones = cur.fetchall()
        telefones_list = [telefone[0] for telefone in telefones]  # Extract the telefone values into a list

        cur.close()
        conn.close()

    # Prepare data for rendering
    cliente_data = {
        'id': cliente[0] if cliente else '',
        'nome': cliente[1] if cliente else '',
        'endereco': cliente[2] if cliente else '',
        'numero': cliente[3] if cliente else '',
        'bairro': cliente[4] if cliente else '',
        'complemento': cliente[5] if cliente else '',
        'municipio': cliente[6] if cliente else '',
        'observacao': cliente[7] if cliente else '',
        'telefones': telefones_list if cliente else []  # Use the telefones_list
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

def insert_cliente(nome, endereco, numero, bairro, complemento, municipio, observacao, telefones):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('''
        INSERT INTO cliente (nome, endereco, numero, bairro, complemento, municipio, observacao)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    ''', (nome, endereco, numero, bairro, complemento, municipio, observacao))
    
    
    cliente_id = cur.fetchone()[0]  # Get the new cliente id
    conn.commit()

    # Insert each telefone into the telefones table
    for telefone in telefones.split(','):
        if telefone:  # Only insert if the telefone is not empty
            cur.execute('''
                INSERT INTO telefones (cliente_id, telefone)
                VALUES (%s, %s)
            ''', (cliente_id, telefone.strip()))

    conn.commit()
    cur.close()
    conn.close()
