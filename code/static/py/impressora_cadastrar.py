# static/py/impressora.py
from flask import Flask, render_template, request, Blueprint, flash, redirect, url_for
import psycopg2
from db import get_db_connection

impressora_cadastrar_bp = Blueprint('impressora_cadastrar_bp', __name__)

@impressora_cadastrar_bp.route('/impressora_cadastrar', methods=['GET', 'POST'])
@impressora_cadastrar_bp.route('/impressora_cadastrar/<int:id>', methods=['GET', 'POST'])
def impressora_cadastrar(id=None):
    if request.method == 'POST':
        id = request.form.get('id', id)
        loja = request.form.get('loja', '')
        descricao = request.form.get('descricao', '')
        endereco = request.form.get('endereco', '')
        tipo_impressao = request.form.get('tipo_impressao', '')
        modelo_impressora = request.form.get('modelo_impressora', '')
        porta = request.form.get('porta', '')
        configuracao = request.form.get('configuracao', '')
        utiliza_guilhotina = request.form.get('utiliza_guilhotina')

        conn = get_db_connection()
        cur = conn.cursor()

        if id:  # If id is provided, check if it exists and then update or insert
            cur.execute('SELECT id FROM impressora WHERE id = %s', (id,))
            existing_client = cur.fetchone()
            if existing_client:
                # Update the existing record
                cur.execute('''
                    UPDATE impressora
                    SET loja = %s, descricao = %s, endereco = %s, tipo_impressao = %s, modelo_impressora = %s, porta = %s, configuracao = %s, utiliza_guilhotina = %s
                    WHERE id = %s
                ''', (loja, descricao, endereco, tipo_impressao, modelo_impressora, porta, configuracao, utiliza_guilhotina, id))
                flash('Impressora atualizada com sucesso', 'success')
            else:
                # Insert a new record if the ID does not exist
                insert_impressora(loja, descricao, endereco, tipo_impressao, modelo_impressora, porta, configuracao, utiliza_guilhotina)
                flash('Impressora cadastrada com sucesso', 'success')
        else:  # If no id is provided, create a new record
            insert_impressora(loja, descricao, endereco, tipo_impressao, modelo_impressora, porta, configuracao, utiliza_guilhotina)
            flash('Impressora cadastrada com sucesso', 'success')

        conn.commit()
        cur.close()
        conn.close()

        return redirect(url_for('pesquisar_impressora_bp.pesquisar_impressora'))

    # GET request: show the form
    impressora = None
    if id:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('SELECT * FROM impressora WHERE id = %s', (id,))
        impressora = cur.fetchone()
        cur.close()
        conn.close()

    # Prepare data for rendering
    impressora_data = {
        'id': impressora[0] if impressora else '',
        'loja': impressora[1] if impressora else '',
        'descricao': impressora[2] if impressora else '',
        'endereco': impressora[3] if impressora else '',
        'tipo_impressao': impressora[4] if impressora else '',
        'modelo_impressora': impressora[5] if impressora else '',
        'porta': impressora[6] if impressora else '',
        'configuracao': impressora[7] if impressora else '',
        'utiliza_guilhotina': impressora[8] if impressora else '',
    }

    next_codigo = get_next_codigo() if impressora is None else impressora[0]
    return render_template('impressora_cadastrar.html', impressora=impressora_data, next_codigo=next_codigo)

def get_next_codigo():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT COALESCE(MAX(id), 0) + 1 FROM impressora')
    next_codigo = cur.fetchone()[0]
    cur.close()
    conn.close()
    return next_codigo

def insert_impressora(loja, descricao, endereco, tipo_impressao, modelo_impressora, porta, configuracao, utiliza_guilhotina):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('''
        INSERT INTO impressora (loja, descricao, endereco, tipo_impressao, modelo_impressora, porta, configuracao, utiliza_guilhotina)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    ''', (loja, descricao, endereco, tipo_impressao, modelo_impressora, porta, configuracao, utiliza_guilhotina))

    conn.commit()
    cur.close()
    conn.close()
