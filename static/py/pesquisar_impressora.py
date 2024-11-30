from flask import Flask, render_template, request, Blueprint, flash, redirect, url_for, jsonify, session
import psycopg2
from static.py.config.db import get_db_connection
from static.py.login_required import login_required

pesquisar_impressora_bp = Blueprint('pesquisar_impressora_bp', __name__)

@pesquisar_impressora_bp.route('/pesquisar_impressora', methods=['GET', 'POST'])
@login_required
def pesquisar_impressora():
    conn = get_db_connection()
    cur = conn.cursor()
    if request.method == 'POST':
        codigo = request.form.get('id', '').strip()
        descricao = request.form.get('descricao', '').strip()
        endereco = request.form.get('endereco', '').strip()
        id_loja = getUserLoja()
        porta = request.form.get('porta', '').strip()
        tipo_impressora = request.form.get('tipo_impressora', '').strip()
        modelo_impressora = request.form.get('modelo_impressora', '').strip()
        if not (codigo or descricao or endereco or porta or tipo_impressora or
                modelo_impressora):
            return jsonify({'error': "Por favor, insira pelo menos um filtro para a pesquisa"}), 400
        query = """
            SELECT id, id_loja, descricao, endereco, porta, tipo_impressora, modelo_impressora, selecionado
            FROM impressora
            WHERE (%s IS NULL OR id = %s)
            AND (%s IS NULL OR id_loja = %s)
            AND (%s IS NULL OR descricao ILIKE %s)
            AND (%s IS NULL OR endereco ILIKE %s)
            AND (%s IS NULL OR porta ILIKE %s)
            AND (%s IS NULL OR tipo_impressora ILIKE %s)
            AND (%s IS NULL OR modelo_impressora ILIKE %s)
        """
        parameters = [
            None if not codigo else int(codigo),
            None if not codigo else int(codigo),
            None if not id_loja else int(id_loja),
            None if not id_loja else int(id_loja),
            None if not descricao else f'%{descricao}%',
            None if not descricao else f'%{descricao}%',
            None if not endereco else f'%{endereco}%',
            None if not endereco else f'%{endereco}%',
            None if not porta else f'%{porta}%',
            None if not porta else f'%{porta}%',
            None if not tipo_impressora else f'%{tipo_impressora}%',
            None if not tipo_impressora else f'%{tipo_impressora}%',
            None if not modelo_impressora else f'%{modelo_impressora}%',
            None if not modelo_impressora else f'%{modelo_impressora}%',
        ]
        try:
            cur.execute(query, parameters)
            impressoras_data = cur.fetchall()
            impressoras = []
            for impressora in impressoras_data:
                impressora_dict = {
                    'id': impressora[0],
                    'descricao': impressora[2],
                    'endereco': impressora[3],
                    'porta': impressora[4],
                    'tipo_impressora': impressora[5],
                    'modelo_impressora': impressora[6],
                    'selecionado': impressora[7]
                }
                impressoras.append(impressora_dict)
            cur.close()
            conn.close()
            if impressoras:
                impressoras.sort(key=lambda row: row['id'])
                return jsonify({'impressoras': impressoras}), 200
            else:
                return jsonify({'error': "Nenhum cliente encontrado"}), 404
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    return render_template('pesquisar_impressora.html')

@pesquisar_impressora_bp.route('/delete_impressora', methods=['POST', 'GET'])
@login_required
def delete_impressora():
    impressora_id = request.form.get('id', '')
    if impressora_id:
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute('DELETE FROM impressora WHERE id = %s', (impressora_id,))
            conn.commit()
            cur.close()
            conn.close()
            flash('impressora deletado com sucesso', 'success')
        except Exception as e:
            print(f"Error occurred: {e}")
            flash('Erro ao deletar impressora', 'error')
    else:
        flash('Nenhum ID de impressora fornecido', 'warning')

    # Redirect to the route within the Blueprint
    return redirect(url_for('pesquisar_impressora_bp.pesquisar_impressora'))

def getUserLoja():
    id_loja = None
    id_operador = session.get('id_operador')
    if id_operador:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute("SELECT id_loja FROM operador WHERE id = %s", (id_operador,))
            id_loja = cursor.fetchone()[0]
        cursor.close()
        conn.close()
    return int(id_loja)
