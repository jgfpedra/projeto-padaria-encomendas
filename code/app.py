from flask import Flask, render_template, request, redirect, url_for, flash
import psycopg2
from psycopg2 import sql
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'default_secret_key')

# Database connection parameters
DATABASE = {
    'dbname': os.getenv('DB_NAME', 'delivery_db'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', 'VrPost@Server'),
    'host': os.getenv('DB_HOST', 'localhost')
}

def get_db_connection():
    conn = psycopg2.connect(**DATABASE)
    return conn

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/pesquisar_cliente')
def pesquisar_cliente():
    return render_template('pesquisar_cliente.html')

@app.route('/cliente_cadastrar')
def cliente_cadastrar():
    return render_template('cliente_cadastrar.html')

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

@app.route('/login_popup')
def login_popup():
    return render_template('/pop-ups/login_popup.html')

if __name__ == '__main__':
    app.run(debug=True)

