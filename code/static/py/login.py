from flask import Blueprint, request, jsonify
import psycopg2
from psycopg2 import sql
from db import get_db_connection

login_bp = Blueprint('login_bp', __name__)

@login_bp.route('/login', methods=['POST'])
def login():
    if request.content_type != 'application/json':
        return jsonify({'error': 'Content-Type must be application/json'}), 400

    data = request.json
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'message': 'Username and password are required'}), 400

    conn = get_db_connection()
    cur = conn.cursor()
    query = sql.SQL("SELECT * FROM operador WHERE login=%s AND senha=%s")
    cur.execute(query, (username, password))

    user = cur.fetchone()
    cur.close()
    conn.close()

    print(user)
    if user:
        return jsonify({'success': True}), 200
    else:
        return jsonify({'success': False, 'message': 'Invalid credentials'}), 401
