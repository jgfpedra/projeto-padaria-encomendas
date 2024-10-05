from flask import Flask, render_template, request, Blueprint, flash, redirect, url_for
import psycopg2
from static.py.config.db import get_db_connection
from static.py.login_required import login_required

pesquisar_cliente_bp = Blueprint('pesquisar_cliente_bp', __name__)

@pesquisar_cliente_bp.route('/pesquisar_cliente', methods=['GET', 'POST'])
@login_required
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
        SELECT c.id, c.nome, c.endereco, c.numero, c.bairro, c.complemento, c.municipio, c.observacao, c.situacao,
               array_agg(t.telefone) AS telefones
        FROM cliente c
        LEFT JOIN telefone t ON c.id = t.cliente_id
        WHERE (%s IS NULL OR c.id = %s)
        AND (%s IS NULL OR c.nome ILIKE %s)
        AND (%s IS NULL OR c.numero ILIKE %s)
        AND (%s IS NULL OR c.municipio ILIKE %s)
        AND (%s IS NULL OR c.endereco ILIKE %s)
        AND (%s IS NULL OR c.situacao ILIKE %s)
        GROUP BY c.id
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

    # Prepare data for rendering, converting telefones to a list if needed
    clientes = []
    for cliente in clientes_data:
        cliente_dict = {
            'id': cliente[0],
            'nome': cliente[1],
            'endereco': cliente[2],
            'numero': cliente[3],
            'bairro': cliente[4],
            'complemento': cliente[5],
            'municipio': cliente[6],
            'observacao': cliente[7],
            'situacao': cliente[8],
            'telefones': cliente[9] if cliente[9] else []  # Handle no telefones case
        }
        clientes.append(cliente_dict)

    if clientes:
        clientes.sort(key=lambda row: row['id'])

    return render_template('pesquisar_cliente.html', clientes=clientes)

@pesquisar_cliente_bp.route('/delete_cliente', methods=['POST', 'GET'])
@login_required
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
