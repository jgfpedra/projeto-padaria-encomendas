from flask import Flask, render_template, request, Blueprint
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
        WHERE (%s = '' OR id = %s)
        AND (%s = '' OR nome ILIKE %s)
        AND (%s = '' OR numero ILIKE %s)
        AND (%s = '' OR municipio ILIKE %s)
        AND (%s = '' OR endereco ILIKE %s)
        AND (%s = '' OR situacao ILIKE %s);
    """
    
    # Execute query with parameters
    cur.execute(query, (
        codigo, int(codigo) if codigo else None,
        nome, f'%{nome}%' if nome else None,
        telefone, f'%{telefone}%' if telefone else None,
        municipio, f'%{municipio}%' if municipio else None,
        endereco, f'%{endereco}%' if endereco else None,
        situacao, f'%{situacao}%' if situacao else None
    ))
        
    clientes_data = cur.fetchall()
    cur.close()
    conn.close()

    return render_template('pesquisar_cliente.html', clientes=clientes_data)

@pesquisar_cliente_bp.route('/delete_cliente', methods=['POST'])
def delete_cliente():
    cliente_id = request.form.get('id')
    if cliente_id:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('DELETE FROM cliente WHERE id = %s', (cliente_id,))
        conn.commit()
        cur.close()
        conn.close()
    return redirect(url_for('clientes'))

@pesquisar_cliente_bp.route('/edit_cliente', methods=['POST'])
def edit_cliente():
    cliente_id = request.form.get('id')
    if cliente_id:
        return redirect(url_for('edit_cliente_form', id=cliente_id))
    return redirect(url_for('clientes'))

@pesquisar_cliente_bp.route('/edit_cliente_form/<int:id>', methods=['GET', 'POST'])
def edit_cliente_form(id):
    conn = get_db_connection()
    cur = conn.cursor()

    if request.method == 'POST':
        nome = request.form.get('nome')
        endereco = request.form.get('endereco')
        numero = request.form.get('numero')
        bairro = request.form.get('bairro')
        complemento = request.form.get('complemento')
        municipio = request.form.get('municipio')
        observacao = request.form.get('observacao')
        telefones = request.form.get('telefones')
        situacao = request.form.get('situacao')

        cur.execute("""
        UPDATE cliente
        SET nome = %s, endereco = %s, numero = %s, bairro = %s, complemento = %s, municipio = %s, observacao = %s, telefones = %s, situacao = %s
        WHERE id = %s
        """, (nome, endereco, numero, bairro, complemento, municipio, observacao, telefones, situacao, id))
        conn.commit()

        cur.close()
        conn.close()
        return redirect(url_for('clientes'))

    cur.execute('SELECT * FROM cliente WHERE id = %s', (id,))
    cliente = cur.fetchone()
    cur.close()
    conn.close()

    return render_template('edit_cliente.html', cliente=cliente)
