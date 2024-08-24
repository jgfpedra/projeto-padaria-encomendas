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

@app.route('/register_user', methods=['GET', 'POST'])
def register_user():
    if request.method == 'POST':
        cellphone = request.form['cellphone']
        address = request.form['address']
        
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute('SELECT * FROM "user" WHERE cellphone = %s', (cellphone,))
        user = cur.fetchone()
        
        if user:
            flash('User already registered.')
            conn.close()
            return redirect(url_for('register_user'))
        
        cur.execute('INSERT INTO "user" (cellphone, address) VALUES (%s, %s)', (cellphone, address))
        conn.commit()
        cur.close()
        conn.close()
        
        flash('User registered successfully.')
        return redirect(url_for('index'))
    
    return render_template('register_user.html')

@app.route('/register_order', methods=['GET', 'POST'])
def register_order():
    if request.method == 'POST':
        cellphone = request.form['cellphone']
        details = request.form['details']
        
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute('SELECT * FROM "user" WHERE cellphone = %s', (cellphone,))
        user = cur.fetchone()
        
        if not user:
            flash('Cellphone not registered.')
            conn.close()
            return redirect(url_for('register_order'))
        
        cur.execute('INSERT INTO "order" (cellphone, details) VALUES (%s, %s)', (cellphone, details))
        conn.commit()
        cur.close()
        conn.close()
        
        flash('Order registered successfully.')
        return redirect(url_for('index'))
    
    return render_template('register_order.html')

@app.route('/manage_orders')
def manage_orders():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM "order"')
    orders = cur.fetchall()
    cur.close()
    conn.close()
    
    return render_template('manage_orders.html', orders=orders)

@app.route('/edit_order/<int:order_id>', methods=['POST'])
def edit_order(order_id):
    new_details = request.form['details']
    
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('UPDATE "order" SET details = %s WHERE id = %s', (new_details, order_id))
    conn.commit()
    cur.close()
    conn.close()
    
    flash('Order updated successfully.')
    return redirect(url_for('manage_orders'))

@app.route('/delete_order/<int:order_id>')
def delete_order(order_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('DELETE FROM "order" WHERE id = %s', (order_id,))
    conn.commit()
    cur.close()
    conn.close()
    
    flash('Order deleted successfully.')
    return redirect(url_for('manage_orders'))

if __name__ == '__main__':
    app.run(debug=True)
