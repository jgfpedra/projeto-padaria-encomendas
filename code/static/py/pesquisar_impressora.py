from flask import Flask, render_template, request, Blueprint, flash, redirect, url_for
import psycopg2
from static.py.config.db import get_db_connection

pesquisar_impressora_bp = Blueprint('pesquisar_impressora_bp', __name__)

@pesquisar_impressora_bp.route('/pesquisar_impressora', methods=['GET', 'POST'])
def pesquisar_impressora():
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Get form inputs
    codigo = request.form.get('id', '')
    loja = request.form.get('loja', '')
    descricao = request.form.get('descricao', '')
    endereco = request.form.get('endereco', '')
    tipo_impressao = request.form.get('tipo_impressao', '')
    modelo_impressora = request.form.get('modelo_impressora', '')
    porta = request.form.get('porta', '')
    configuracao = request.form.get('configuracao', '')
    utiliza_guilhotina = request.form.get('utiliza_guilhotina', '')

    # Build query with filters
    query = """
        SELECT id, loja, descricao, endereco, tipo_impressao, modelo_impressora, porta, configuracao, utiliza_guilhotina
        FROM impressora
        WHERE (%s IS NULL OR id = %s)
        AND (%s IS NULL OR loja = %s)
        AND (%s IS NULL OR descricao ILIKE %s)
        AND (%s IS NULL OR endereco ILIKE %s)
        AND (%s IS NULL OR tipo_impressao ILIKE %s)
        AND (%s IS NULL OR modelo_impressora ILIKE %s)
        AND (%s IS NULL OR porta ILIKE %s)
        AND (%s IS NULL OR configuracao ILIKE %s)
        AND (%s IS NULL OR utiliza_guilhotina = %s);
    """

    # Define parameters for the query
    parameters = [
        None if not codigo else int(codigo),
        None if not codigo else int(codigo),
        None if not loja else f'%{loja}%',
        None if not loja else f'%{loja}%',
        None if not descricao else f'%{descricao}%',
        None if not descricao else f'%{descricao}%',
        None if not endereco else f'%{endereco}%',
        None if not endereco else f'%{endereco}%',
        None if not tipo_impressao else f'%{tipo_impressao}%',
        None if not tipo_impressao else f'%{tipo_impressao}%',
        None if not modelo_impressora else f'%{modelo_impressora}%',
        None if not modelo_impressora else f'%{modelo_impressora}%',
        None if not porta else f'%{porta}%',
        None if not porta else f'%{porta}%',
        None if not configuracao else f'%{configuracao}%',
        None if not configuracao else f'%{configuracao}%',
        None if not utiliza_guilhotina else f'%{utiliza_guilhotina}%',
        None if not utiliza_guilhotina else f'%{utiliza_guilhotina}%',
    ]

    # Execute query with parameters
    cur.execute(query, parameters)
    impressoras_data = cur.fetchall()
    cur.close()
    conn.close()

    return render_template('pesquisar_impressora.html', impressoras=impressoras_data)

@pesquisar_impressora_bp.route('/delete_impressora', methods=['POST', 'GET'])
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
