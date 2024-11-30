from flask import Flask, render_template, request, Blueprint, flash, redirect, url_for, jsonify
import psycopg2
from static.py.config.db import get_db_connection
from static.py.login_required import login_required
import re

pesquisar_cliente_bp = Blueprint('pesquisar_cliente_bp', __name__)

@pesquisar_cliente_bp.route('/pesquisar_cliente', methods=['GET', 'POST'])
@login_required
def pesquisar_cliente():
    conn = get_db_connection()
    cur = conn.cursor()
    
    if request.method == 'POST':
        codigo = request.form.get('id', '').strip()
        nome = request.form.get('nome', '').strip()
        telefone = request.form.get('telefone', '').strip()
        endereco = request.form.get('endereco', '').strip()

        # Check if at least one filter is provided
        if not (codigo or nome or telefone or endereco):
            return jsonify({'error': "Por favor, insira pelo menos um filtro para a pesquisa."}), 400

        # Construct the base query
        query = """
            SELECT c.id, c.nome, c.endereco, c.numero, c.bairro, c.complemento, c.observacao,
                array_agg(t.telefone) AS telefones
            FROM cliente c
            LEFT JOIN telefone t ON c.id = t.cliente_id
        """
        
        # List to hold parameters
        parameters = []

        # Add conditions based on the provided filters
        query_conditions = ["WHERE 1=1"]  # Base condition to make it easier to add more
        
        if codigo:
            query_conditions.append(" AND c.id = %s")
            parameters.append(int(codigo))
        if nome:
            query_conditions.append(" AND c.nome ILIKE %s")
            parameters.append(f'%{nome}%')
        if telefone:
            query_conditions.append(" AND (t.telefone ILIKE %s OR c.id IN (SELECT cliente_id FROM telefone WHERE telefone ILIKE %s))")
            parameters.append(f'%{telefone}%')
            parameters.append(f'%{telefone}%')  # To match the condition for the subquery
        if endereco:
            query_conditions.append(" AND c.endereco ILIKE %s")
            parameters.append(f'%{endereco}%')
        
        query += " ".join(query_conditions)

        # Add GROUP BY clause to aggregate phone numbers
        query += """
            GROUP BY c.id
        """

        try:
            # Execute the query with dynamic parameters
            cur.execute(query, parameters)
            clientes_data = cur.fetchall()

            # Prepare the results
            clientes = []
            for cliente in clientes_data:
                cliente_dict = {
                    'id': cliente[0],
                    'nome': cliente[1],
                    'endereco': cliente[2],
                    'numero': cliente[3],
                    'bairro': cliente[4],
                    'complemento': cliente[5],
                    'observacao': cliente[6],
                    'telefones': cliente[7] if cliente[7] else []  # Ensure telefones is not None
                }
                clientes.append(cliente_dict)

            cur.close()
            conn.close()
            # Return the result
            if clientes:
                clientes.sort(key=lambda row: row['id'])
                return jsonify({'clientes': clientes}), 200
            else:
                return jsonify({'error': "Nenhum cliente encontrado"}), 404
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    return render_template('pesquisar_cliente.html')

@pesquisar_cliente_bp.route('/delete_cliente', methods=['POST', 'GET'])
@login_required
def delete_cliente():
    cliente_id = request.form.get('id', '')
    print(cliente_id)
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

    return redirect(url_for('pesquisar_cliente_bp.pesquisar_cliente'))
