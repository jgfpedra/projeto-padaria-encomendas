from flask import Flask, render_template, request, Blueprint, flash, redirect, url_for, session, jsonify
import psycopg2
from static.py.config.db import get_db_connection
from static.py.config.db_vr import get_db_vr
from static.py.login_required import login_required
from datetime import datetime
from decimal import Decimal
from printer import print_receipt, format_receipt_encomenda

encomenda_bp = Blueprint('encomenda_bp', __name__)

def get_client(conn, cellphone):
    with conn.cursor() as cur:
        query = "SELECT cliente_id FROM telefone WHERE telefone = %s"
        cur.execute(query, (cellphone,))
        clients = cur.fetchone()
        if clients:
            return clients[0]
        else:
            raise ValueError("No valid cellphone numbers found")

def add_encomenda(conn, situacao, data_encomenda, hora_encomenda, tipo, loja, client_id, data_criacao, hora_criacao):
    with conn.cursor() as cur:
        cur.execute("SELECT data_criacao, encomenda_id FROM encomenda ORDER BY id DESC LIMIT 1")
        last_order_data = cur.fetchone()

        if last_order_data:  # Check if last_order_data is not empty
            last_date = last_order_data[0]  # Unpack the first element of the outer tuple
            last_id = last_order_data[1]
            if last_date == data_criacao:
                encomenda_id = last_id + 1
            else:
                encomenda_id = 1  # Default logic
        else:
            encomenda_id = 1

        cur.execute("""INSERT INTO encomenda (situacao, data_encomenda, hora_encomenda,
            tipo, loja, cliente_id, encomenda_id, data_criacao, hora_criacao) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)""",
            (situacao, data_encomenda, hora_encomenda, tipo, loja, client_id, encomenda_id, data_criacao, hora_criacao))
        conn.commit()
        return encomenda_id, data_criacao

def add_item_to_encomenda(conn, encomenda_id, product_id, quantity, valor_item, valor_item_total, date):
    with conn.cursor() as cur:
        if date:
            cur.execute("SELECT data_criacao, hora_criacao FROM encomenda WHERE encomenda_id = %s AND data_criacao = %s", (encomenda_id, date))
            data_hora_criacao = cur.fetchone()
        else:
            data_criacao = datetime.now().date()
            cur.execute("SELECT data_criacao, hora_criacao FROM encomenda WHERE encomenda_id = %s AND data_criacao = %s", (encomenda_id, data_criacao))
            data_hora_criacao = cur.fetchone()
        cur.execute("SELECT quantidade FROM itens_encomenda WHERE id_encomenda = %s AND id_produtos = %s AND data_criacao = %s AND hora_criacao = %s", (encomenda_id, product_id, data_hora_criacao[0], data_hora_criacao[1]))
        existing_item = cur.fetchone()
        if existing_item:
            new_quantity = float(existing_item[0]) + float(quantity)
            cur.execute("UPDATE itens_encomenda SET quantidade = %s WHERE id_encomenda = %s AND id_produtos = %s AND data_criacao = %s AND hora_criacao = %s",
                        (new_quantity, encomenda_id, product_id, data_hora_criacao[0], data_hora_criacao[1]))
        else:
            cur.execute("INSERT INTO itens_encomenda (id_encomenda, id_produtos, quantidade, valor_item_total, valor_item, data_criacao, hora_criacao) "
                        "VALUES (%s, %s, %s, %s, %s, %s, %s)",
                        (encomenda_id, product_id, quantity, valor_item_total, valor_item, data_hora_criacao[0], data_hora_criacao[1]))
        conn.commit()

def fetch_encomenda(conn, encomenda_id, parsed_date):
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM encomenda WHERE encomenda_id = %s AND data_criacao = %s", (encomenda_id, parsed_date))
        return cur.fetchone()

def fetch_observacao(conn, id_itens_encomenda, item_id):
    with conn.cursor() as cur:
        cur.execute("""
        SELECT observacao
        FROM observacao
        WHERE id_itens_encomenda = %s
        AND id_item_produto = %s
        """, (id_itens_encomenda, item_id,))
        result = cur.fetchone()

        if result:
            return result[0]
        else:
            return None

def fetch_products(conn, conn_vr, itens_data):
    products = {}
    with conn_vr.cursor() as cur_vr:
        for item in itens_data:
            itens_encomenda_id, item_id, quantity = item[0], item[2], item[3]
            observacao = (fetch_observacao(conn, itens_encomenda_id, item_id) or None)
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
                        'total': 0,
                        'itens_encomenda_id': itens_encomenda_id,
                    }
                products[codigo]['quantidade'] += round(quantity, 3)
                products[codigo]['total'] = round(products[codigo]['quantidade'], 3) * round(products[codigo]['preco_venda'], 2)
                products[codigo]['total'] = round(products[codigo]['total'], 2)

                if observacao:
                    products[codigo]['observacao'] = observacao
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
        dados = cur.fetchone()
        cur.execute("SELECT telefone FROM telefone WHERE cliente_id = %s", (client_id,))
        telefone = cur.fetchall()
        results = {
            'dados': dados,
            'telefone': telefone
        }
        return results

def fetch_itens_encomenda(conn, encomenda_id, parsed_date):
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM itens_encomenda WHERE id_encomenda = %s AND data_criacao = %s", (encomenda_id, parsed_date))
        return (cur.fetchall() or [])

def calculate_totals(products, encomenda_data):
    subtotal = sum(Decimal(item['total']) for item in products.values())
    valor_entrega = Decimal(encomenda_data[7]) if encomenda_data[7] is not None else Decimal('0.00')
    desconto = Decimal(encomenda_data[8]) if encomenda_data[8] is not None else Decimal('0.00')
    total = subtotal + valor_entrega - desconto
    return subtotal, valor_entrega, desconto, total

def update_encomenda(conn, encomenda_id, subtotal, parsed_date):
    with conn.cursor() as cur:
        cur.execute("""
            UPDATE encomenda 
            SET subtotal = %s
            WHERE encomenda_id = %s
            AND data_criacao = %s
        """, (subtotal, encomenda_id, parsed_date))
        conn.commit()

def fetch_encomenda_data(conn, conn_vr, encomenda_id, parsed_date):
    context = initialize_context()
    encomenda_data = fetch_encomenda(conn, encomenda_id, parsed_date)
    if encomenda_data:
        itens_data = fetch_itens_encomenda(conn, encomenda_id, parsed_date)
        products = fetch_products(conn, conn_vr, itens_data)
        cliente_data = fetch_cliente(conn, encomenda_data[6])

        subtotal, valor_entrega, desconto, total = calculate_totals(products, encomenda_data)

        update_encomenda(conn, encomenda_id, subtotal, parsed_date)

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
            session.pop('product_id', None)

def handle_product_addition(conn_vr, conn, date, encomenda_id):
    if encomenda_id:
        product_id = request.form.get('product_id', '')
        quantity = request.form.get('quantity', '')

        if product_id and not quantity:
            session['encomenda_id'] = encomenda_id
            session['date'] = date
            session['product_id'] = int(product_id)
            handle_product_id(conn_vr, product_id, encomenda_id)

        elif quantity and 'product_id' in session:
            try:
                print(quantity)
                valor_item = fetch_product_price(conn_vr.cursor(), session['product_id'])
                valor_item_total = valor_item * Decimal(quantity)
                add_item_to_encomenda(conn, encomenda_id, session['product_id'], quantity, valor_item, valor_item_total, date)
                session.pop('product_id', None)
                flash('Product added successfully.', 'success')
            except Exception as e:
                flash(f'Error adding product: {e}', 'error')

def handle_post_requests(conn, conn_vr, date, encomenda_id):
    if 'cellphone' in request.form:
        return handle_cellphone_request(conn, encomenda_id)
    if session.get('client_id') and 'orderType' in request.form:
        return handle_tipo_encomenda(conn, encomenda_id)
    if 'finalizar' in request.form:
        return handle_finalize_request(encomenda_id)
    if session.get('finalizar', False):
        return handle_finalization(conn, conn_vr, encomenda_id)
    if session.get('client_id'):
        session.pop('client_id')
    handle_product_addition(conn_vr, conn, date, encomenda_id)
    return False

def handle_cellphone_request(conn, encomenda_id):
    cellphone = request.form.get('cellphone')
    try:
        client_id = get_client(conn, cellphone)
        session['client_id'] = client_id
    except ValueError as e:
        flash(str(e), 'error')
        return False
    return True

def handle_tipo_encomenda(conn, encomenda_id):
    order_type = request.form.get('orderType')
    entrega_date = request.form.get('entregaDate')
    entrega_time = request.form.get('entregaTime')

    if order_type == 'entrega' and entrega_date and entrega_time:
        encomenda_id, date = create_encomenda(conn, session['client_id'], entrega_date, entrega_time)
    else:
        encomenda_id, date = create_encomenda(conn, session['client_id'])  # Default to Retirada
    session['encomenda_id'] = encomenda_id
    session['date'] = date
    session.pop('client_id')
    return True

def create_encomenda(conn, client_id, data_encomenda=None, hora_encomenda=None):
    data_criacao = datetime.now().date()
    hora_criacao = datetime.now().time()
    situacao = 'Digitando'
    if data_encomenda is None:
        data_encomenda = datetime.now().date()
        tipo = "Retirada"
    else:
        tipo = "Entrega"

    if hora_encomenda is None:
        hora_encomenda = datetime.now().time()
    loja = 1
    return add_encomenda(conn, situacao, data_encomenda, hora_encomenda, tipo, loja, client_id, data_criacao, hora_criacao)

def handle_finalize_request(encomenda_id, data):
    session['finalizar'] = True
    session['encomenda_id'] = encomenda_id
    session['date'] = data
    return redirect(url_for('encomenda_bp.encomenda', date=session['date'], encomenda_id=session['encomenda_id']))

def handle_finalization(conn, conn_vr, encomenda_id):
    if 'valor_entrega' in request.form and 'desconto' in request.form:
        try:
            valor_entrega = Decimal(request.form.get('valor_entrega', 0.00))
            desconto = Decimal(request.form.get('desconto', 0.00))
            finalize_encomenda(conn, encomenda_id, valor_entrega, desconto)
            receipt_text = format_receipt_encomenda(conn, conn_vr, encomenda_id, date)
            print_receipt(receipt_text)
            session.pop('finalizar', None)
            return redirect(url_for('encomenda_bp.encomenda'))
        except ValueError:
            flash('Invalid value for "valor_entrega" or "desconto".', 'error')
    else:
        flash('Both "valor_entrega" and "desconto" are required.', 'error')
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
                SET situacao = %s, valor_entrega = %s, desconto = %s, total = %s, subtotal = %s
                WHERE encomenda_id = %s AND data_criacao = %s
            """, ("Finalizado", valor_entrega, desconto, total, subtotal, encomenda_id, data))
            conn.commit()
    except Exception as e:
        print(f"Error finalizing encomenda: {e}")

def update_item_observacao(conn, itens_encomenda_id, id_produto, nova_observacao):
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM observacao WHERE id_itens_encomenda = %s AND id_item_produto = %s", 
                    (itens_encomenda_id, id_produto))
        existing_observation = cur.fetchone()

        if existing_observation:
            cur.execute("""
                UPDATE observacao 
                SET observacao = %s 
                WHERE id_itens_encomenda = %s AND id_item_produto = %s
            """, (nova_observacao, itens_encomenda_id, id_produto))
        else:
            cur.execute("""
                INSERT INTO observacao (id_itens_encomenda, id_item_produto, observacao) 
                VALUES (%s, %s, %s)
            """, (itens_encomenda_id, id_produto, nova_observacao))
        
        conn.commit()

@encomenda_bp.route('/update_observacao', methods=['POST'])
@login_required
def update_observacao():
    conn = get_db_connection()
    data = request.get_json()
    try:
        itens_encomenda_id = data.get('itens_encomenda_id')
        id_produto = data.get('id_produto')
        nova_observacao = data.get('nova_observacao')

        if itens_encomenda_id and id_produto and nova_observacao:
            update_item_observacao(conn, itens_encomenda_id, id_produto, nova_observacao)
            flash('Observation updated successfully.', 'success')
        else:
            flash('All fields are required.', 'error')

    except Exception as e:
        flash(f'An error occurred: {e}', 'error')
    finally:
        conn.close()
    return redirect(url_for('encomenda_bp.encomenda', encomenda_id=session.get('encomenda_id')))

@encomenda_bp.route('/delete_observacao', methods=['POST'])
@login_required
def delete_observacao():
    data = request.get_json()
    itens_encomenda_id = data.get('itens_encomenda_id')
    id_produto = data.get('id_produto')
    delete_observation_from_db(itens_encomenda_id, id_produto)
    return jsonify({"message": "Observation deleted successfully."}), 200

def delete_observation_from_db(itens_encomenda_id, id_produto):
    conn = get_db_connection()
    with conn.cursor() as cur:
        cur.execute("""
            DELETE FROM observacao
            WHERE id_itens_encomenda = %s AND id_item_produto = %s
        """, (itens_encomenda_id, id_produto))
    conn.commit()

@encomenda_bp.route('/delete_item', methods=['POST'])
@login_required
def delete_item():
    data = request.json
    itens_encomenda_id = data.get('itens_encomenda_id')
    id_produto = data.get('id_produto')
    date = data.get('date')
    if not itens_encomenda_id or not id_produto or not date:
        return jsonify({"error": "Missing data"}), 400
    delete_item_from_db(itens_encomenda_id, id_produto, date)
    return jsonify({"message": "Item deleted successfully."}), 200

def delete_item_from_db(itens_encomenda_id, id_produto, date):
    conn = get_db_connection()
    with conn.cursor() as cur:
        cur.execute("""
            DELETE FROM itens_encomenda
            WHERE id = %s AND id_produtos = %s AND data_criacao = %s
        """, (itens_encomenda_id, id_produto, date))
    conn.commit()

@encomenda_bp.route('/imprimir_encomenda', methods=['POST'])
@login_required
def imprimir_encomenda():
    conn = get_db_connection()
    conn_vr = get_db_vr()
    data = request.json
    encomenda_id = data.get('encomenda_id')
    date = data.get('date')
    if not itens_encomenda_id or not id_produto or not date:
        return jsonify({"error": "Missing data"}), 400
    receipt_text = format_receipt_encomenda(conn, conn_vr, encomenda_id, date)
    print_receipt(receipt_text)
    return jsonify({"message": "Item deleted successfully."}), 200

@encomenda_bp.route('/encomenda', methods=['GET', 'POST'])
@encomenda_bp.route('/encomenda/<string:date>/<int:encomenda_id>', methods=['GET', 'POST'])
@login_required
def encomenda(date=None, encomenda_id=None):
    conn = get_db_connection()
    conn_vr = get_db_vr()
    context = initialize_context()
    try:
        if date:
            try:
                parsed_date = datetime.strptime(date, '%Y-%m-%d').date()
            except Exception as e:
                flash('Invalid date format.', 'error')
                return redirect(url_for('encomenda_bp.encomenda'))
        session['encomenda_id'] = encomenda_id
        session['date'] = date
        if request.method == 'POST':
            if handle_post_requests(conn, conn_vr, date, encomenda_id):
                return redirect(url_for('encomenda_bp.encomenda',
                                        date=session.get('date'),
                                        encomenda_id=session.get('encomenda_id')))
        if encomenda_id:
            context.update(fetch_encomenda_data(conn, conn_vr, encomenda_id, parsed_date))
    except Exception as e:
        flash(f'An error occurred: {e}', 'error')
    finally:
        conn.close()
        conn_vr.close()
    return render_template('encomenda.html', **context)
