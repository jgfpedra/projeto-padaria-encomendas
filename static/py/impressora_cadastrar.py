from flask import Flask, render_template, request, Blueprint, flash, redirect, url_for, jsonify
import psycopg2
import serial.tools.list_ports
from static.py.config.db import get_db_connection
from static.py.login_required import login_required

impressora_cadastrar_bp = Blueprint('impressora_cadastrar_bp', __name__)

@impressora_cadastrar_bp.route('/impressora_cadastrar', methods=['GET', 'POST'])
@impressora_cadastrar_bp.route('/impressora_cadastrar/<int:id>', methods=['GET', 'POST'])
@login_required
def impressora_cadastrar(id=None):
    if request.method == 'POST':
        loja = request.form.get('loja', '')
        descricao = request.form.get('descricao', '')
        endereco = request.form.get('endereco', '')
        tipo_impressora = request.form.get('tipo_impressora', '')
        modelo_impressora = request.form.get('modelo_impressora', '')
        porta = request.form.get('porta', '')
        utiliza_guilhotina = request.form.get('utiliza_guilhotina', '')

        if not porta:
            porta = None

        # verifica se já existe uma impressora com o mesmo ip e porta
        if verifica_impressora_existente(endereco, porta, id):
            return jsonify({'success': True, 'message': 'já existe uma impressora com esse ip e porta.'}), 400

        # if there's an id, update the impressora; otherwise, create a new one
        if id:  # update existing impressora
            cur = get_db_connection().cursor()
            cur.execute('SELECT id FROM impressora WHERE id = %s', (id,))
            existing_impressora = cur.fetchone()
            if existing_impressora:
                cur.execute('''
                    update impressora
                    set loja = %s, descricao = %s, endereco = %s, tipo_impressora = %s, modelo_impressora = %s, porta = %s, utiliza_guilhotina = %s
                    where id = %s
                ''', (loja, descricao, endereco, tipo_impressora, modelo_impressora, porta, utiliza_guilhotina, id))
                get_db_connection().commit()
                cur.close()
                return jsonify({'success': True, 'message': 'impressora updated successfully'})
            else:
                return jsonify({'success': False, 'message': 'impressora not found'}), 404
        else:  # create new impressora
            insert_impressora(loja, descricao, endereco, tipo_impressora, modelo_impressora, porta, utiliza_guilhotina)
            return jsonify({'success': True, 'message': 'impressora created successfully'})

    # for get request or after failed submission, render the form
    impressora = None
    next_codigo = None

    if id:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('SELECT * FROM impressora WHERE id = %s', (id,))
        impressora = cur.fetchone()
        cur.close()
        conn.close()
    else:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('SELECT last_value FROM impressora_id_seq')  # get the last value of the sequence
        last_value = cur.fetchone()[0]
        if(last_value == 1):
            next_codigo = last_value
        else:
            next_codigo = last_value + 1  # increment the value to get the next available id
        cur.close()
        conn.close()

    impressora_data = {
        'id': impressora[0] if impressora else '',
        'id_loja': impressora[1] if impressora else '',
        'descricao': impressora[2] if impressora  else '',
        'endereco': impressora[3] if impressora else '',
        'tipo_impressora': impressora[4] if impressora else '',
        'modelo_impressora': impressora[5] if impressora else '',
        'porta': impressora[6] if impressora else '',
        'utiliza_guilhotina': impressora[7] if impressora else '',
    }

    portas = [port.device for port in serial.tools.list_ports.comports()]

    return render_template('impressora_cadastrar.html', impressora=impressora_data, next_codigo=next_codigo, portas=portas)


def insert_impressora(loja, descricao, endereco, tipo_impressora, modelo_impressora, porta, utiliza_guilhotina):
    conn = get_db_connection()
    cur = conn.cursor()

    # if porta is empty, set it to none for sql insert
    if not porta:
        porta = None

    cur.execute('''
        insert into impressora (loja, descricao, endereco, tipo_impressora, modelo_impressora, porta, utiliza_guilhotina)
        values (%s, %s, %s, %s, %s, %s, %s)
    ''', (loja, descricao, endereco, tipo_impressora, modelo_impressora, porta, utiliza_guilhotina))

    conn.commit()
    cur.close()
    conn.close()


def verifica_impressora_existente(endereco, porta, id=None):
    conn = get_db_connection()
    cur = conn.cursor()

    # se id for fornecido, exclui da verificação (para não se comparar consigo mesmo)
    if id:
        cur.execute('''
            select 1 from impressora
            where endereco = %s and porta = %s and id != %s
        ''', (endereco, porta, id))
    else:
        cur.execute('''
            select 1 from impressora
            where endereco = %s and porta = %s
        ''', (endereco, porta))

    # se uma linha for retornada, significa que já existe uma impressora com o mesmo ip e porta
    result = cur.fetchone()
    cur.close()
    conn.close()

    return result is not None
