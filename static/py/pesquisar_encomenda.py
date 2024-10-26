from flask import Flask, render_template, request, Blueprint, flash, redirect, url_for
import psycopg2
from datetime import datetime, date
from decimal import Decimal
from static.py.config.db import get_db_connection
from static.py.login_required import login_required

pesquisar_encomenda_bp = Blueprint('pesquisar_encomenda_bp', __name__)

@pesquisar_encomenda_bp.route('/pesquisar_encomenda', methods=['GET', 'POST'])
@login_required
def pesquisar_encomenda():
    conn = get_db_connection()
    cur = conn.cursor()

    # Get form inputs
    encomenda_id = request.form.get('encomenda_id', '')
    tipo = request.form.get('tipo', '')
    data_inicial_criacao = request.form.get('data_inicial_criacao', '')
    data_final_criacao = request.form.get('data_final_criacao', '')
    data_inicial_encomenda = request.form.get('data_inicial_encomenda', '')
    data_final_encomenda = request.form.get('data_final_encomenda', '')
    cliente_id = request.form.get('cliente_id', '')
    nome_cliente = request.form.get('nome_cliente', '')
    total = request.form.get('total', '')
    telefone = request.form.get('telefone', '')
    situacao = request.form.get('situacao', '')

    # Set default dates for data_inicial_criacao and data_final_criacao if not provided
    if not data_inicial_criacao and not data_final_criacao:
        today = date.today()
        data_inicial_criacao = today.strftime('%Y-%m-%d')
        data_final_criacao = today.strftime('%Y-%m-%d')

    # Build the query
    query = """
        SELECT e.encomenda_id, e.tipo, e.situacao, e.data_criacao, e.data_encomenda,
        c.id, c.nome, e.total, STRING_AGG(t.telefone, ', ') AS telefones
        FROM encomenda e
        INNER JOIN cliente c ON e.cliente_id = c.id
        LEFT JOIN telefone t ON c.id = t.cliente_id
        WHERE 1=1
    """

    # Initialize a list for parameters
    parameters = []

    # Add filters only if the corresponding value is provided
    if encomenda_id.strip():
        query += " AND e.encomenda_id = %s"
        parameters.append(int(encomenda_id))

    if tipo.strip():
        query += " AND e.tipo ILIKE %s"
        parameters.append(f'%{tipo}%')

    if situacao.strip():
        query += " AND e.situacao = %s"
        parameters.append(situacao)

    if data_inicial_criacao.strip() and data_final_criacao.strip():
        query += " AND e.data_criacao BETWEEN %s AND %s"
        parameters.append(datetime.strptime(data_inicial_criacao, '%Y-%m-%d').date())
        parameters.append(datetime.strptime(data_final_criacao, '%Y-%m-%d').date())

    if data_inicial_encomenda.strip() and data_final_encomenda.strip():
        query += " AND e.data_encomenda BETWEEN %s AND %s"
        parameters.append(datetime.strptime(data_inicial_encomenda, '%Y-%m-%d').date())
        parameters.append(datetime.strptime(data_final_encomenda, '%Y-%m-%d').date())

    if cliente_id.strip():
        query += " AND e.cliente_id = %s"
        parameters.append(int(cliente_id))

    if nome_cliente.strip():
        query += " AND c.nome ILIKE %s"
        parameters.append(f'%{nome_cliente}%')

    if total.strip():
        query += " AND e.total = %s"
        parameters.append(Decimal(total))

    if telefone.strip():
        query += " AND t.telefone ILIKE %s"
        parameters.append(f'%{telefone}%')

    # Try executing the query
    try:
        query += """
            GROUP BY e.encomenda_id, e.tipo, e.situacao, e.data_criacao, e.data_encomenda, c.id, c.nome, e.total
        """
        cur.execute(query, parameters)
        encomendas_data = cur.fetchall()
        # Check if any data was returned
        if not encomendas_data:
            flash("Nenhuma encomenda encontrada para os critérios especificados.", "warning")
        else:
            # Sort encomendas_data by desired column (replace 'encomenda_id' with your preference)
            encomendas_data.sort(key=lambda row: row[0])

    except Exception as e:
        flash(f"Ocorreu um erro: {str(e)}", "danger")
        encomendas_data = []  # Ensure it doesn't throw an error when rendering

    finally:
        cur.close()
        conn.close()

    return render_template('pesquisar_encomenda.html', encomendas=encomendas_data)
