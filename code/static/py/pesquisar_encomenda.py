from flask import Flask, render_template, request, Blueprint, flash, redirect, url_for
import psycopg2
from datetime import datetime
from decimal import Decimal
from static.py.config.db import get_db_connection

pesquisar_encomenda_bp = Blueprint('pesquisar_encomenda_bp', __name__)

@pesquisar_encomenda_bp.route('/pesquisar_encomenda', methods=['GET', 'POST'])
def pesquisar_encomenda():
    conn = get_db_connection()
    cur = conn.cursor()

    # Get form inputs
    codigo = request.form.get('id', '')
    data_hora_criacao = request.form.get('data_hora_criacao', '')
    situacao = request.form.get('situacao', '')
    data_encomenda = request.form.get('data_encomenda', '')
    hora_encomenda = request.form.get('hora_encomenda', '')
    tipo = request.form.get('tipo', '')
    loja = request.form.get('loja', '')
    cliente_id = request.form.get('cliente_id', '')
    valor_entrega = request.form.get('valor_entrega', '')
    desconto = request.form.get('desconto', '')
    total = request.form.get('total', '')
    subtotal = request.form.get('subtotal', '')
    encomenda_id = request.form.get('encomenda_id', '')

    # Build query with filters
    query = """
        SELECT id, data_hora_criacao, situacao, data_encomenda, hora_encomenda,
        tipo, loja, cliente_id, valor_entrega, desconto, total, subtotal,
        encomenda_id
        FROM encomenda
        WHERE (%s IS NULL OR id = %s)
        AND (%s IS NULL OR data_hora_criacao = %s)
        AND (%s IS NULL OR situacao ILIKE %s)
        AND (%s IS NULL OR data_encomenda = %s)
        AND (%s IS NULL OR hora_encomenda = %s)
        AND (%s IS NULL OR tipo ILIKE %s)
        AND (%s IS NULL OR loja = %s)
        AND (%s IS NULL OR cliente_id = %s)
        AND (%s IS NULL OR valor_entrega = %s)
        AND (%s IS NULL OR desconto = %s)
        AND (%s IS NULL OR total = %s)
        AND (%s IS NULL OR subtotal = %s)
        AND (%s IS NULL OR encomenda_id = %s)
    """

    # Prepare parameters for the query
    parameters = [
        None if not codigo else int(codigo),
        None if not codigo else int(codigo),
        None if not data_hora_criacao else datetime.strptime(data_hora_criacao, '%Y-%m-%d %H:%M:%S'),
        None if not data_hora_criacao else datetime.strptime(data_hora_criacao, '%Y-%m-%d %H:%M:%S'),
        None if not situacao else f'%{situacao}%',
        None if not situacao else f'%{situacao}%',
        None if not data_encomenda else datetime.strptime(data_encomenda, '%Y-%m-%d').date(),
        None if not data_encomenda else datetime.strptime(data_encomenda, '%Y-%m-%d').date(),
        None if not hora_encomenda else datetime.strptime(hora_encomenda, '%H:%M:%S').time(),
        None if not hora_encomenda else datetime.strptime(hora_encomenda, '%H:%M:%S').time(),
        None if not tipo else f'%{tipo}%',
        None if not tipo else f'%{tipo}%',
        None if not loja else int(loja),
        None if not loja else int(loja),
        None if not cliente_id else int(cliente_id),
        None if not cliente_id else int(cliente_id),
        None if not valor_entrega else Decimal(valor_entrega),
        None if not valor_entrega else Decimal(valor_entrega),
        None if not desconto else Decimal(desconto),
        None if not desconto else Decimal(desconto),
        None if not total else Decimal(total),
        None if not total else Decimal(total),
        None if not subtotal else Decimal(subtotal),
        None if not subtotal else Decimal(subtotal),
        None if not encomenda_id else int(encomenda_id),
        None if not encomenda_id else int(encomenda_id),
    ]

    # Execute query with parameters
    cur.execute(query, parameters)
    encomendas_data = cur.fetchall()
    cur.close()
    conn.close()

    return render_template('pesquisar_encomenda.html', encomendas=encomendas_data)
