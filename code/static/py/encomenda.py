from flask import Flask, render_template, request, Blueprint, flash, redirect, url_for
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


from flask import render_template, request, flash, redirect, url_for, session
from datetime import datetime

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
        'product_id': None  # Initialize product_id in context
    }

    try:
        if request.method == 'POST':
            if encomenda_id:
                product_id = request.form.get('product_id', '')
                quantity = request.form.get('quantity', '')

                if product_id and not quantity:
                    # Save product_id to session or context
                    session['product_id'] = product_id
                    flash('Product ID received. Please enter the quantity.', 'info')
                    return redirect(url_for('encomenda_bp.encomenda', encomenda_id=encomenda_id))
                elif quantity and 'product_id' in session:
                    # Retrieve and remove the product ID from the session
                    product_id = session.pop('product_id')
                    
                    if quantity:
                        add_item_to_encomenda(conn, encomenda_id, product_id, quantity)
                        conn.commit()
                        flash('Product added to encomenda!', 'success')
                        # Reset product_id after adding to encomenda
                        context['product_id'] = None
                        return redirect(url_for('encomenda_bp.encomenda', encomenda_id=encomenda_id))
                    else:
                        flash('Invalid quantity.', 'error')
                else:
                    flash('Invalid product ID or quantity.', 'error')

            else:
                # Create a new encomenda
                cellphone = request.form.get('cellphone', '')
                now = datetime.now()
                data_hora_criacao = now.strftime('%d-%m-%Y %H:%M:%S')
                situacao = "Em andamento"
                data_encomenda = now.strftime('%d-%m-%Y')
                hora_encomenda = now.strftime('%H:%M:%S')
                tipo = "Entrega"
                loja = 1

                with conn.cursor() as cur:
                    cur.execute("SELECT id FROM cliente WHERE telefones ILIKE %s", (f'%{cellphone}%',))
                    cliente = cur.fetchone()

                if cliente:
                    client_id = cliente[0]
                    encomenda_id = add_encomenda(conn, data_hora_criacao, situacao, data_encomenda, hora_encomenda, tipo, loja, client_id)
                    
                    if encomenda_id:
                        flash('Encomenda added successfully!', 'success')
                        return redirect(url_for('encomenda_bp.encomenda', encomenda_id=encomenda_id))
                else:
                    flash('Cellphone not found in the database.', 'error')

        if encomenda_id:
            # Fetch encomenda data
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM encomenda WHERE id = %s", (encomenda_id,))
                encomenda_data = cur.fetchone()

                # Fetch items data
                cur.execute("SELECT * FROM itens_encomenda WHERE id_encomenda = %s", (encomenda_id,))
                itens_data = cur.fetchall() or []

            # Aggregate product data
            products = {}
            
            with conn_vr.cursor() as cur_vr:
                for item in itens_data:
                    item_id = item[2]  # Assuming item[2] contains the product ID
                    quantity = item[3]  # Assuming item[3] contains the quantity

                    # Fetch the price for the specific item
                    cur_vr.execute("SELECT precovenda FROM venda WHERE id_produto = %s ORDER BY id DESC LIMIT 1", (item_id,))
                    preco_result = cur_vr.fetchone()
                    preco = float(preco_result[0]) if preco_result else 0.00
                    
                    # Fetch product information
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
                        
                        # Update quantity and total
                        products[codigo]['quantidade'] += quantity
                        products[codigo]['total'] = products[codigo]['quantidade'] * products[codigo]['preco_venda']

            # Convert the aggregated products data into a list of dictionaries
            products_list = list(products.values())

            # Fetch client details
            if encomenda_data:
                client_id = encomenda_data[7]
                with conn.cursor() as cur:
                    cur.execute("SELECT * FROM cliente WHERE id = %s", (client_id,))
                    cliente_data = cur.fetchone()  # Use fetchone for a single record

            # Compute totals
            subtotal = sum(item['total'] for item in products_list)
            valor_entrega = 10.00
            desconto = 5.00
            total = subtotal + valor_entrega - desconto

            context.update({
                'encomenda': encomenda_data,
                'cliente': cliente_data,  # Update context with client data
                'itens': products_list,
                'subtotal': round(subtotal, 2),
                'valor_entrega': round(valor_entrega, 2),
                'desconto': round(desconto, 2),
                'total': round(total, 2),
                'product_id': session.get('product_id')  # Pass product_id from session
            })

    except Exception as e:
        flash(f'An error occurred: {e}', 'error')

    finally:
        conn.close()
        conn_vr.close()

    return render_template('encomenda.html', **context)
