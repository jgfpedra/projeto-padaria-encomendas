from flask import Flask, render_template, request, redirect, url_for, flash
import psycopg2
from psycopg2 import sql

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'

# Database connection parameters
DATABASE = {
    'dbname': 'delivery_db',
    'user': 'postgres',
    'password': 'VrPost@Server',
    'host': 'localhost'
}

def get_db_connection():
    conn = psycopg2.connect(**DATABASE)
    return conn

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/cliente.cadastrar')
def cliente_cadastrar():
    print()

@app.route('/impressora.cadastrar')
def impressora_cadastrar():
    print()

@app.route('/encomendas')
def encomendas():
    print()

@app.route('/pesquisar.encomendas')
def pesquisar_encomendas():
    print()

@app.route('/impressora.configuracao')
def impressora_configuracao():
    print()

if __name__ == '__main__':
    app.run(debug=True)
