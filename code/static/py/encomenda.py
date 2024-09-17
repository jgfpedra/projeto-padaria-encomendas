from flask import Flask, render_template, request, Blueprint, flash, redirect, url_for, session, jsonify
import psycopg2
from db import get_db_connection
from db_vr import get_db_vr
from datetime import datetime

encomenda_bp = Blueprint('encomenda_bp',__name__)

def add_encomenda(conn, data_hora_criacao, situacao, data_encomenda, hora_encomenda, tipo, loja, client_id):
    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO encomenda (data_hora_criacao, situacao, data_encomenda, hora_encomenda, tipo, loja, cliente_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING id
        """, (data_hora_criacao, situacao, data_encomenda, hora_encomenda, tipo, loja, client_id))
        encomenda_id = cur.fetchone()[0]
        conn.commit()

        return encomenda_id

def add_item_to_encomenda(conn, encomenda_id, product_id, quantity):
    with conn.cursor() as cur:
        cur.execute("INSERT INTO itens_encomenda (id_encomenda, id_produtos, quantidade) VALUES (%s, %s, %s)",
                    (encomenda_id, product_id, quantity))
        conn.commit()

def fetch_encomenda_data(conn, conn_vr, encomenda_id):
    context = {
        'encomenda': None,
        'itens': [],
        'cliente': None,
        'subtotal': 0.00,
        'valor_entrega': 0.00,
        'desconto': 0.00,
        'total': 0.00,
        'product_id': None,
        'tipoembalagem': 'DEFAULT',
        'finalizar': False
    }

    with conn.cursor() as cur:
        cur.execute("SELECT * FROM encomenda WHERE id = %s", (encomenda_id,))
        encomenda_data = cur.fetchone()

        if encomenda_data:
            cur.execute("SELECT * FROM itens_encomenda WHERE id_encomenda = %s", (encomenda_id,))
            itens_data = cur.fetchall() or []

            products = {}
            with conn_vr.cursor() as cur_vr:
                for item in itens_data:
                    item_id = item[2]
                    quantity = item[3]

                    cur_vr.execute("SELECT precovenda FROM venda WHERE id_produto = %s ORDER BY id DESC LIMIT 1", (item_id,))
                    preco_result = cur_vr.fetchone()
                    preco = float(preco_result[0]) if preco_result else 0.00

                    cur_vr.execute("SELECT id, descricaoreduzida FROM produto WHERE id = %s", (item_id,))
                    product_info = cur_vr.fetchone()

                    if product_info:
                        codigo, descricaoreduzida = product_info
                        if codigo not in products:
                            products[codigo] = {
                                'codigo': codigo,
                                'descricaoreduzida': descricaoreduzida,
                                'quantidade': 0,
                                'preco_venda': preco,
                                'total': 0
                            }

                        products[codigo]['quantidade'] += round(quantity, 3)
                        products[codigo]['total'] = round(products[codigo]['quantidade'], 3) * round(products[codigo]['preco_venda'], 2)
                        products[codigo]['total'] = round(products[codigo]['total'], 2)

            products_list = list(products.values())

            client_id = encomenda_data[7]
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM cliente WHERE id = %s", (client_id,))
                cliente_data = cur.fetchone()

            subtotal = sum(item['total'] for item in products_list)
            valor_entrega = encomenda_data[4] if encomenda_data[4] is not None else 0.00
            desconto = encomenda_data[5] if encomenda_data[5] is not None else 0.00
            total = subtotal + valor_entrega - desconto

            context.update({
                'encomenda': encomenda_data,
                'cliente': cliente_data,
                'itens': products_list,
                'subtotal': round(subtotal, 2),
                'valor_entrega': round(valor_entrega, 2),
                'desconto': round(desconto, 2),
                'total': round(total, 2),
                'product_id': session.get('product_id'),
                'tipoembalagem': session.get('tipoembalagem', 'DEFAULT'),
                'finalizar': session.get('finalizar', False)
            })
    
    return context

def handle_product_id(conn, product_id, encomenda_id):
    with conn.cursor() as cur:
        cur.execute("SELECT id_tipoembalagem FROM produto WHERE id = %s", (product_id,))
        id_tipoembalagem = cur.fetchone()

        if id_tipoembalagem:
            cur.execute("SELECT descricao FROM tipoembalagem WHERE id = %s", (id_tipoembalagem[0],))
            tipoembalagem = cur.fetchone()
            if tipoembalagem:
                session['tipoembalagem'] = tipoembalagem[0]
                flash('Product ID received. Please enter the quantity.', 'info')
            else:
                flash('Packaging type not found.', 'error')
        else:
            flash('Product ID not found.', 'error')


def handle_product_addition(conn, encomenda_id):
    if encomenda_id:
        product_id = request.form.get('product_id', '')
        quantity = request.form.get('quantity', '')

        if product_id and not quantity:
            session['product_id'] = product_id
            handle_product_id(conn, product_id, encomenda_id)

        elif quantity and 'product_id' in session:
            product_id = session.pop('product_id')
            tipoembalagem = session.pop('tipoembalagem', None)
            if quantity and tipoembalagem:
                add_item_to_encomenda(conn, encomenda_id, product_id, quantity)
                conn.commit()

def handle_post_requests(conn, encomenda_id):
    if 'finalizar' in request.form:
        session['finalizar'] = True
        return True

    if session.get('finalizar', False):
        if 'valor_entrega' in request.form and 'desconto' in request.form:
            try:
                valor_entrega = float(request.form.get('valor_entrega', 0.00))
                desconto = float(request.form.get('desconto', 0.00))
                finalize_encomenda(conn, encomenda_id, valor_entrega, desconto)
                flash('Encomenda finalized successfully!', 'success')
                session.pop('finalizar', None)
                return True
            except ValueError:
                flash('Invalid value for "valor_entrega" or "desconto".', 'error')
        else:
            flash('Both "valor_entrega" and "desconto" are required.', 'error')

    handle_product_addition(conn, encomenda_id)
    return False

def get_encomenda_details(conn, conn_vr, encomenda_id):
    context = {}
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM encomenda WHERE id = %s", (encomenda_id,))
        encomenda_data = cur.fetchone()

        if encomenda_data:
            cur.execute("SELECT * FROM itens_encomenda WHERE id_encomenda = %s", (encomenda_id,))
            itens_data = cur.fetchall() or []

            products = get_product_details(conn_vr, itens_data)
            products_list = list(products.values())

            client_id = encomenda_data[7]
            cur.execute("SELECT * FROM cliente WHERE id = %s", (client_id,))
            cliente_data = cur.fetchone()

            subtotal = sum(item['total'] for item in products_list)
            valor_entrega = encomenda_data[4]  # Fetch from database if saved
            desconto = encomenda_data[5]       # Fetch from database if saved
            total = subtotal + valor_entrega - desconto

            context.update({
                'encomenda': encomenda_data,
                'cliente': cliente_data,
                'itens': products_list,
                'subtotal': round(subtotal, 2),
                'valor_entrega': round(valor_entrega, 2),
                'desconto': round(desconto, 2),
                'total': round(total, 2),
                'product_id': session.get('product_id'),
                'tipoembalagem': session.get('tipoembalagem', 'DEFAULT'),
                'finalizar': session.get('finalizar', False)
            })
    return context

def get_product_details(conn_vr, itens_data):
    products = {}
    with conn_vr.cursor() as cur_vr:
        for item in itens_data:
            item_id = item[2]
            quantity = item[3]

            cur_vr.execute("SELECT precovenda FROM venda WHERE id_produto = %s ORDER BY id DESC LIMIT 1", (item_id,))
            preco_result = cur_vr.fetchone()
            preco = float(preco_result[0]) if preco_result else 0.00

            cur_vr.execute("SELECT id, descricaoreduzida FROM produto WHERE id = %s", (item_id,))
            product_info = cur_vr.fetchone()

            if product_info:
                codigo, descricaoreduzida = product_info
                if codigo not in products:
                    products[codigo] = {
                        'codigo': codigo,
                        'descricaoreduzida': descricaoreduzida,
                        'quantidade': 0,
                        'preco_venda': preco,
                        'total': 0
                    }

                products[codigo]['quantidade'] += round(quantity, 3)
                products[codigo]['total'] = round(products[codigo]['quantidade'], 3) * round(products[codigo]['preco_venda'], 2)
                products[codigo]['total'] = round(products[codigo]['total'], 2)
    return products

def finalize_encomenda(conn, encomenda_id, valor_entrega, desconto):
    with conn.cursor() as cur:
        cur.execute("SELECT subtotal FROM encomenda WHERE id = %s", (encomenda_id,))
        result = cur.fetchone()
        if result:
            existing_subtotal = result[0] if result[0] is not None else 0.00
        else:
            existing_subtotal = 0.00  # Default if no record found

        subtotal = existing_subtotal
        total = subtotal + valor_entrega - desconto

        cur.execute("""
            UPDATE encomenda 
            SET valor_entrega = %s, desconto = %s, subtotal = %s, total = %s
            WHERE id = %s
        """, (valor_entrega, desconto, subtotal, total, encomenda_id))
        conn.commit()

@encomenda_bp.route('/encomenda', methods=['GET', 'POST'])
@encomenda_bp.route('/encomenda/<int:encomenda_id>', methods=['GET', 'POST'])
def encomenda(encomenda_id=None):
    conn = get_db_connection()
    conn_vr = get_db_vr()
    context = {
        'encomenda': None,
        'itens': [],
        'cliente': None,
        'subtotal': 0.00,
        'valor_entrega': 0.00,
        'desconto': 0.00,
        'total': 0.00,
        'product_id': None,
        'tipoembalagem': 'DEFAULT',
        'finalizar': False
    }

    try:
        if request.method == 'POST':
            if handle_post_requests(conn, encomenda_id):
                return redirect(url_for('encomenda_bp.encomenda', encomenda_id=encomenda_id))

        if encomenda_id:
            context.update(fetch_encomenda_data(conn, conn_vr, encomenda_id))

    except Exception as e:
        flash(f'An error occurred: {e}', 'error')

    finally:
        conn.close()
        conn_vr.close()

    return render_template('encomenda.html', **context)

