# app.py
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session, send_from_directory
import sys
import os
import importlib.util
from flask_cors import CORS
from static.py.login_required import login_required

def load_secret_key(file_path):
    with open(file_path, 'r') as file:
        return file.read().strip()

app = Flask(__name__)
app.secret_key = load_secret_key('static/py/config/secret_key.txt')

# Set the session cookie settings
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'  # or 'Strict', or 'None' for cross-site usage
app.config['SESSION_COOKIE_SECURE'] = True  # Use only over HTTPS (recommended for 'None')

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
cliente_cadastrar_bp = modules['cliente_cadastrar']
login_bp = modules['login']
pesquisar_cliente_bp = modules['pesquisar_cliente']
impressora_cadastrar_bp = modules['impressora_cadastrar']
pesquisar_impressora_bp = modules['pesquisar_impressora']
encomenda_bp = modules['encomenda']
pesquisar_encomenda_bp = modules['pesquisar_encomenda']
impressora_configurar_bp = modules['configurar_impressora']

app.register_blueprint(login_bp.login_bp)
app.register_blueprint(pesquisar_cliente_bp.pesquisar_cliente_bp)
app.register_blueprint(cliente_cadastrar_bp.cliente_cadastrar_bp)
app.register_blueprint(impressora_cadastrar_bp.impressora_cadastrar_bp)
app.register_blueprint(pesquisar_impressora_bp.pesquisar_impressora_bp)
app.register_blueprint(encomenda_bp.encomenda_bp)
app.register_blueprint(pesquisar_encomenda_bp.pesquisar_encomenda_bp)
app.register_blueprint(impressora_configurar_bp.impressora_configurar_bp)

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(app.root_path + '/static', 'favicon.ico')

@app.route('/')
@login_required
def index():
    return render_template('index.html')

@app.route('/impressora_configuracao')
@login_required
def impressora_configuracao():
    return render_template('impressora_configuracao.html')

@app.route('/login_popup', methods=['POST'])
@login_required
def show_popup_login():
    popup_html = render_template('pop-ups/login_popup.html')
    return jsonify({'popup_html': popup_html})

@app.route('/lancamento_finalizar_encomendas')
@login_required
def show_popup_lancamento_finalizar_encomendas():
    popup_html_finalizar = render_template('pop-ups/lancamento_finalizar_encomendas.html')
    return jsonify({'popup_html_finalizar': popup_html_finalizar})

@app.route('/lancamento_historico_encomendas')
@login_required
def show_popup_lancamento_historico_encomendas():
    popup_html = render_template('pop-ups/lancamento_historico_encomendas.html')
    return jsonify({'popup_html': popup_html})

@app.route('/lancamento_salvar_encomendas')
@login_required
def show_popup_lancamento_salvar_encomendas():
    popup_html = render_template('pop-ups/lancamento_salvar_encomendas.html')
    return jsonify({'popup_html': popup_html})

@app.route('/salvar_cliente_cadastrar')
@login_required
def show_popup_salvar_cliente_cadastrar():
    popup_html = render_template('pop-ups/salvar_cliente_cadastrar.html')
    return jsonify({'popup_html': popup_html})

@app.route('/salvar_impressora_cadastrar')
@login_required
def show_popup_salvar_impressora_cadastrar():
    popup_html = render_template('pop-ups/salvar_impressora_cadastrar.html')
    return jsonify({'popup_html': popup_html})

if __name__ == '__main__':
    app.run(debug=True)

