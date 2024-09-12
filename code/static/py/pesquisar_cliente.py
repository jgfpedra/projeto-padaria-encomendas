from flask import Flask, render_template, request, Blueprint, flash, redirect, url_for
import psycopg2
from db import get_db_connection

pesquisar_cliente_bp = Blueprint('pesquisar_cliente_bp', __name__)

@pesquisar_cliente_bp.route('/pesquisar_cliente', methods=['GET', 'POST'])
def pesquisar_cliente():
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Get form inputs
    codigo = request.form.get('codigo', '')
    nome = request.form.get('nome', '')
    telefone = request.form.get('telefone', '')
    municipio = request.form.get('municipio', '')
    endereco = request.form.get('endereco', '')
    situacao = request.form.get('situacao', '')

    # Build query with filters
    query = """
        SELECT id, nome, endereco, numero, bairro, complemento, municipio, observacao, telefones, situacao
        FROM cliente
        WHERE (%s IS NULL OR id = %s)
        AND (%s IS NULL OR nome ILIKE %s)
        AND (%s IS NULL OR numero ILIKE %s)
        AND (%s IS NULL OR municipio ILIKE %s)
        AND (%s IS NULL OR endereco ILIKE %s)
        AND (%s IS NULL OR situacao ILIKE %s);
    """

    # Define parameters for the query
    parameters = [
        None if not codigo else int(codigo),
        None if not codigo else int(codigo),
        None if not nome else f'%{nome}%',
        None if not nome else f'%{nome}%',
        None if not telefone else f'%{telefone}%',
        None if not telefone else f'%{telefone}%',
        None if not municipio else f'%{municipio}%',
        None if not municipio else f'%{municipio}%',
        None if not endereco else f'%{endereco}%',
        None if not endereco else f'%{endereco}%',
        None if not situacao else f'%{situacao}%',
        None if not situacao else f'%{situacao}%'
    ]

    # Execute query with parameters
    cur.execute(query, parameters)
    
    clientes_data = cur.fetchall()
    cur.close()
    conn.close()

    return render_template('pesquisar_cliente.html', clientes=clientes_data)

@pesquisar_cliente_bp.route('/delete_cliente', methods=['POST', 'GET'])
def delete_cliente():
    cliente_id = request.form.get('id', '')
    if cliente_id:
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute('DELETE FROM cliente WHERE id = %s', (cliente_id,))
            conn.commit()
            cur.close()
            conn.close()
            flash('Cliente deletado com sucesso', 'success')
        except Exception as e:
            print(f"Error occurred: {e}")
            flash('Erro ao deletar cliente', 'error')
    else:
        flash('Nenhum ID de cliente fornecido', 'warning')

    # Redirect to the route within the Blueprint
    return redirect(url_for('pesquisar_cliente_bp.pesquisar_cliente'))
