# app.py
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import sys
import os
import importlib.util

app = Flask(__name__)

# Define the directory containing your Python modules
module_dir = os.path.join(os.path.dirname(__file__), 'static/py')

# Add the directory to the system path
sys.path.append(module_dir)

def import_all_modules(directory):
    modules = {}
    for filename in os.listdir(directory):
        if filename.endswith('.py') and filename != '__init__.py':
            module_name = filename[:-3]  # Strip the .py extension
            file_path = os.path.join(directory, filename)
            
            # Load the module
            spec = importlib.util.spec_from_file_location(module_name, file_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Save the module in the dictionary
            modules[module_name] = module
    return modules

# Import all modules from the static/py directory
modules = import_all_modules(module_dir)

# Assuming cliente is one of the imported modules
cliente_cc = modules['cadastrar_cliente']
login_bp = modules['login']
pesquisar_cliente_bp = modules['pesquisar_cliente']

app.register_blueprint(login_bp.login_bp)
app.register_blueprint(pesquisar_cliente_bp.pesquisar_cliente_bp)

# Create the table if it doesn't exist
cliente_cc.create_table()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login_page')
def login_page():
    return render_template('login.html')

@app.route('/cliente_cadastrar', methods=['GET', 'POST'])
@app.route('/cliente_cadastrar/<int:id>', methods=['GET', 'POST'])
def cliente_cadastrar(id=None):
    if request.method == 'POST':
        id = request.form.get('id', '')
        nome = request.form.get('nome', '')
        endereco = request.form.get('endereco', '')
        numero = request.form.get('numero', '')
        bairro = request.form.get('bairro', '')
        complemento = request.form.get('complemento', '')
        municipio = request.form.get('municipio', '')
        observacao = request.form.get('observacao', '')
        telefones = ','.join(request.form.getlist('telefones'))

        if id:  # If id is provided, update the existing record
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute('''
                UPDATE cliente
                SET nome = %s, endereco = %s, numero = %s, bairro = %s, complemento = %s, municipio = %s, observacao = %s, telefones = %s
                WHERE id = %s
            ''', (nome, endereco, numero, bairro, complemento, municipio, observacao, telefones, id))
            conn.commit()
            cur.close()
            conn.close()
        else:  # If no id is provided, create a new record
            insert_cliente(nome, endereco, numero, bairro, complemento, municipio, observacao, telefones)
        return redirect(url_for('clientes'))

    # GET request: show the form
    id = request.args.get('id')
    if id:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('SELECT * FROM cliente WHERE id = %s', (id,))
        cliente = cur.fetchone()
        cur.close()
        conn.close()
        cliente = {
            'id': cliente[0],
            'nome': cliente[1],
            'endereco': cliente[2],
            'numero': cliente[3],
            'bairro': cliente[4],
            'complemento': cliente[5],
            'municipio': cliente[6],
            'observacao': cliente[7],
            'telefones': cliente[8]
        }
    else:
        cliente = None

    next_codigo = cliente_cc.get_next_codigo()
    return render_template('cliente_cadastrar.html', cliente=cliente, next_codigo=next_codigo)

@app.route('/pesquisar_impressrora')
def pesquisar_impressora():
    return render_template('pesquisar_impressora.html')

@app.route('/impressora_cadastrar')
def impressora_cadastrar():
    return render_template('impressora_cadastrar.html')

@app.route('/encomendas')
def encomendas():
    return render_template('encomendas.html')

@app.route('/pesquisar_encomendas')
def pesquisar_encomendas():
    return render_template('pesquisar_encomendas.html')

@app.route('/impressora_configuracao')
def impressora_configuracao():
    return render_template('impressora_configuracao.html')

@app.route('/login_popup', methods=['POST'])
def show_popup_login():
    popup_html = render_template('pop-ups/login_popup.html')
    return jsonify({'popup_html': popup_html})

@app.route('/impressora_configurar_popup')
def show_popup_impressora():
    popup_html = render_template('pop-ups/impressora_configurar_popup.html')
    return jsonify({'popup_html': popup_html})

@app.route('/lancamento_finalizar_encomendas')
def show_popup_lancamento_finalizar_encomendas():
    popup_html = render_template('pop-ups/lancamento_finalizar_encomendas.html')
    return jsonify({'popup_html': popup_html})

@app.route('/lancamento_historico_encomendas')
def show_popup_lancamento_historico_encomendas():
    popup_html = render_template('pop-ups/lancamento_historico_encomendas.html')
    return jsonify({'popup_html': popup_html})

@app.route('/lancamento_salvar_encomendas')
def show_popup_lancamento_salvar_encomendas():
    popup_html = render_template('pop-ups/lancamento_salvar_encomendas.html')
    return jsonify({'popup_html': popup_html})

@app.route('/salvar_cliente_cadastrar')
def show_popup_salvar_cliente_cadastrar():
    popup_html = render_template('pop-ups/salvar_cliente_cadastrar.html')
    return jsonify({'popup_html': popup_html})

@app.route('/salvar_impressora_cadastrar')
def show_popup_salvar_impressora_cadastrar():
    popup_html = render_template('pop-ups/salvar_impressora_cadastrar.html')
    return jsonify({'popup_html': popup_html})

if __name__ == '__main__':
    app.run(debug=True)

