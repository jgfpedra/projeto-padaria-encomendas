from flask import Flask, render_template, request, Blueprint, flash, redirect, url_for, session, jsonify
import psycopg2
from static.py.config.db import get_db_connection
from static.py.config.db_vr import get_db_vr
from datetime import datetime
from decimal import Decimal
from printer import print_receipt, format_receipt_encomenda

encomenda_bp = Blueprint('encomenda_bp', __name__)

def get_client(conn, cellphone):
    with conn.cursor() as cur:
        # Prepare the query to find a client with the provided phone number
        query = "SELECT cliente_id FROM telefone WHERE telefone = %s"
        cur.execute(query, (cellphone,))  # Use a tuple to pass the parameter
        clients = cur.fetchone()
        if clients:
            return clients[0]  # Return the first client's ID found
        else:
            raise ValueError("No valid cellphone numbers found")  # Raise an error if no client found

def add_encomenda(conn, situacao, data_encomenda, hora_encomenda, tipo, loja, client_id, data_criacao, hora_criacao):
    with conn.cursor() as cur:
        # Fetch the last order's creation date
        cur.execute("SELECT data_criacao, encomenda_id FROM encomenda ORDER BY id desc limit 1")
        last_order_data = cur.fetchone()

        print(last_order_data)
        # Reset or increment encomenda_id based on the comparison
        if last_order_data == None:
            encomenda_id = 1  # Reset if the last order is from a different
        elif last_order_data[0] == data_criacao:
            encomenda_id = int(last_order_data[1]) + 1  # Increment if the last order is from today

        print(encomenda_id)
        cur.execute("""INSERT INTO encomenda (situacao, data_encomenda, hora_encomenda,
            tipo, loja, cliente_id, encomenda_id, data_criacao, hora_criacao) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)""",
            (situacao, data_encomenda, hora_encomenda, tipo, loja, client_id, encomenda_id, data_criacao, hora_criacao))
        conn.commit()

        return encomenda_id

def add_item_to_encomenda(conn, encomenda_id, product_id, quantity, valor_item, valor_item_total):
    with conn.cursor() as cur:
        data_criacao = datetime.now().date()
        cur.execute("SELECT data_criacao, hora_criacao FROM encomenda WHERE encomenda_id = %s AND data_criacao = %s", (encomenda_id, data_criacao, ))
        data_hora_criacao = cur.fetchone()
        cur.execute("INSERT INTO itens_encomenda (id_encomenda, id_produtos, quantidade, valor_item_total, valor_item, data_criacao, hora_criacao) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                    (encomenda_id, product_id, quantity,
                     valor_item_total, valor_item, data_hora_criacao[0], data_hora_criacao[1]))
        conn.commit()

def fetch_encomenda_data(conn, conn_vr, encomenda_id):
    context = initialize_context()

    encomenda_data = fetch_encomenda(conn, encomenda_id)
    if encomenda_data:
        itens_data = fetch_itens_encomenda(conn, encomenda_id)
        products = fetch_products(conn_vr, itens_data)
        cliente_data = fetch_cliente(conn, encomenda_data[6])

        subtotal, valor_entrega, desconto, total = calculate_totals(products, encomenda_data)

        update_encomenda(conn, encomenda_id, subtotal)

        context.update({
            'encomenda': encomenda_data,
            'cliente': cliente_data,
            'itens': list(products.values()),
            'subtotal': round(subtotal, 2),
            'valor_entrega': round(valor_entrega, 2),
            'desconto': round(desconto, 2),
            'total': round(total, 2),
            'product_id': session.get('product_id'),
            'tipoembalagem': session.get('tipoembalagem', 'DEFAULT'),
            'finalizar': session.get('finalizar', False)
        })
    
    return context

def initialize_context():
    return {
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

def fetch_encomenda(conn, encomenda_id):
    with conn.cursor() as cur:
        data = datetime.now().date()
        cur.execute("SELECT * FROM encomenda WHERE encomenda_id = %s AND data_criacao = %s", (encomenda_id, data))
        return cur.fetchone()

def fetch_itens_encomenda(conn, encomenda_id):
    with conn.cursor() as cur:
        data = datetime.now().date()
        cur.execute("SELECT * FROM itens_encomenda WHERE id_encomenda = %s AND data_criacao = %s", (encomenda_id, data))
        return cur.fetchall() or []

def fetch_products(conn_vr, itens_data):
    products = {}
    with conn_vr.cursor() as cur_vr:
        for item in itens_data:
            item_id, quantity = item[2], item[3]
            preco = fetch_product_price(cur_vr, item_id)
            product_info = fetch_product_info(cur_vr, item_id)

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

def fetch_product_price(cur_vr, item_id):
    cur_vr.execute("SELECT precovenda FROM venda WHERE id_produto = %s ORDER BY id DESC LIMIT 1", (item_id,))
    preco_result = cur_vr.fetchone()
    return Decimal(preco_result[0]) if preco_result else Decimal('0.00')

def fetch_product_info(cur_vr, item_id):
    cur_vr.execute("SELECT id, descricaoreduzida FROM produto WHERE id = %s", (item_id,))
    return cur_vr.fetchone()

def fetch_cliente(conn, client_id):
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM cliente WHERE id = %s", (client_id,))
        return cur.fetchone()

def calculate_totals(products, encomenda_data):
    subtotal = sum(Decimal(item['total']) for item in products.values())
    valor_entrega = Decimal(encomenda_data[7]) if encomenda_data[7] is not None else Decimal('0.00')
    desconto = Decimal(encomenda_data[8]) if encomenda_data[8] is not None else Decimal('0.00')
    total = subtotal + valor_entrega - desconto
    return subtotal, valor_entrega, desconto, total

def update_encomenda(conn, encomenda_id, subtotal):
    with conn.cursor() as cur:
        cur.execute("""
            UPDATE encomenda 
            SET subtotal = %s
            WHERE id = %s
        """, (subtotal, encomenda_id))
        conn.commit()

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
            session.pop('product_id', None)  # Remove product_id from session if not found

def handle_product_addition(conn_vr, conn, encomenda_id):
    if encomenda_id:
        product_id = request.form.get('product_id', '')
        quantity = request.form.get('quantity', '')

        if product_id and not quantity:
            session['product_id'] = int(product_id)
            handle_product_id(conn_vr, product_id, encomenda_id)

        elif quantity and 'product_id' in session:
            with conn_vr.cursor() as cur:
                cur.execute("SELECT precovenda FROM venda WHERE id_produto = %s ORDER BY id DESC LIMIT 1", (session['product_id'],))
                valor_item = Decimal(cur.fetchone()[0])
                valor_item_total = Decimal(valor_item) * Decimal(quantity)
                product_id = session.pop('product_id', None)
                tipoembalagem = session.pop('tipoembalagem', None)

        if quantity and tipoembalagem:
            add_item_to_encomenda(conn, encomenda_id, product_id, quantity, valor_item, valor_item_total)

def handle_post_requests(conn, conn_vr, encomenda_id):
    if 'cellphone' in request.form:
        cellphone = request.form.get('cellphone')
        try:
            client_id = get_client(conn, cellphone)
        except ValueError as e:
            flash(str(e), 'error')  # Flash the error message
            return False  # Indicate that an error occurred

        data_criacao = datetime.now().date()
        hora_criacao = datetime.now().time()
        situacao = 'Digitando'
        data_encomenda = datetime.now().date()
        hora_encomenda = datetime.now().time()
        tipo = 'Entrega'
        loja = 1

        encomenda_id = add_encomenda(conn, situacao, data_encomenda, hora_encomenda, tipo, loja, client_id, data_criacao, hora_criacao)
        session['encomenda_id'] = encomenda_id
        return True  # Indicate success

    if 'finalizar' in request.form:
        session['finalizar'] = True
        session['encomenda_id'] = encomenda_id
        return redirect(url_for('encomenda_bp.encomenda', encomenda_id=encomenda_id))

    if session.get('finalizar', False):
        if 'valor_entrega' in request.form and 'desconto' in request.form:
            try:
                valor_entrega = Decimal(request.form.get('valor_entrega', 0.00))
                desconto = Decimal(request.form.get('desconto', 0.00))
                finalize_encomenda(conn, encomenda_id, valor_entrega, desconto)
                # Create the formatted receipt text
                receipt_text = format_receipt_encomenda(conn, conn_vr, encomenda_id)
                print_receipt(receipt_text)
                session.pop('finalizar', None)
                return redirect(url_for('encomenda_bp.encomenda'))  # Redirect to the base URL
            except ValueError:
                flash('Invalid value for "valor_entrega" or "desconto".', 'error')
        else:
            flash('Both "valor_entrega" and "desconto" are required.', 'error')

    handle_product_addition(conn_vr, conn, encomenda_id)
    return False


def finalize_encomenda(conn, encomenda_id, valor_entrega, desconto):
    try:
        with conn.cursor() as cur:
            data = datetime.now().date()
            cur.execute("SELECT subtotal FROM encomenda WHERE encomenda_id = %s AND data_criacao = %s", (encomenda_id, data))
            result = cur.fetchone()
            existing_subtotal = result[0] if result else 0.00
            subtotal = existing_subtotal
            total = Decimal(subtotal) + Decimal(valor_entrega) - Decimal(desconto)
            cur.execute("""
                UPDATE encomenda 
                SET valor_entrega = %s, desconto = %s, total = %s, subtotal = %s
                WHERE encomenda_id = %s AND data_criacao = %s
            """, (valor_entrega, desconto, total, subtotal, encomenda_id, data))
            conn.commit()
    except Exception as e:
        print(f"Error finalizing encomenda: {e}")

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
            if handle_post_requests(conn, conn_vr, encomenda_id):
                return redirect(url_for('encomenda_bp.encomenda', encomenda_id=session['encomenda_id']))

        if encomenda_id:
            context.update(fetch_encomenda_data(conn, conn_vr, encomenda_id))
    except Exception as e:
        flash(f'An error occurred: {e}', 'error')
    finally:
        conn.close()
        conn_vr.close()

    return render_template('encomenda.html', **context)
