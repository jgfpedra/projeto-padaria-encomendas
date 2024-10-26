from flask import Blueprint, request, jsonify, session, render_template
import psycopg2
from psycopg2 import sql
from static.py.config.db import get_db_connection

login_bp = Blueprint('login_bp', __name__)

# GET route for rendering the login page
@login_bp.route('/login', methods=['GET'])
def login_page():
    return render_template('login.html')  # Render the login form

# POST route for processing login
@login_bp.route('/login', methods=['POST'])
def login():
    if request.content_type != 'application/json':
        return jsonify({'error': 'Content-Type must be application/json'}), 400

    data = request.json
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'message': 'Username and password are required'}), 400

    # Connect to the database
    conn = get_db_connection()
    cur = conn.cursor()

    # Use parameterized queries to prevent SQL injection
    query = sql.SQL("SELECT * FROM operador WHERE login=%s")
    cur.execute(query, (username,))
    user = cur.fetchone()

    cur.close()
    conn.close()

    if user:
        stored_password = user[2]  # Assuming password is in the fourth column (index 3)

        print(stored_password)
        # Compare passwords directly
        if password == stored_password:
            session['logged_in'] = True  # Store user session
            return jsonify({'success': True}), 200
        else:
            return jsonify({'success': False, 'message': 'Invalid credentials'}), 401
    else:
        return jsonify({'success': False, 'message': 'Invalid credentials'}), 401

@login_bp.route('/logout', methods=['GET'])
def logout_page():
    return render_template('login.html')  # Render the login form

@login_bp.route('/logout', methods=['POST'])
def logout():
    session.pop('logged_in', None)  # Remove user session
    return jsonify({'success': True}), 200
