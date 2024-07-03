from flask import Flask, render_template, redirect, url_for, request, session
from functools import wraps
import sqlite3

app = Flask(__name__)
app.secret_key = 'supersecretkey'

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('role') != 'admin':
            return redirect(url_for('home'))
        return f(*args, **kwargs)
    return decorated_function

def staff_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('role') not in ['admin', 'staff']:
            return redirect(url_for('home'))
        return f(*args, **kwargs)
    return decorated_function

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/menu', methods=['GET', 'POST'])
def menu():
    if 'cart' not in session:
        session['cart'] = []

    if request.method == 'POST':
        item_name = request.form['item_name']
        item_description = request.form['item_description']
        item_price = request.form['item_price']
        item_quantity = int(request.form['quantity'])

        cart_item = {
            'name': item_name,
            'description': item_description,
            'price': float(item_price),
            'quantity': item_quantity
        }

        session['cart'].append(cart_item)
        session.modified = True
        return redirect(url_for('menu'))

    menu_items = {
        'Przystawki': [
            {'name': 'Przystawka 1', 'description': 'Opis przystawki 1', 'price': 20, 'image': 'przystawka1.jpg'},
            {'name': 'Przystawka 2', 'description': 'Opis przystawki 2', 'price': 25, 'image': 'przystawka2.jpg'},
        ],
        'Dania główne': [
            {'name': 'Danie główne 1', 'description': 'Opis dania głównego 1', 'price': 40, 'image': 'danie1.jpg'},
            {'name': 'Danie główne 2', 'description': 'Opis dania głównego 2', 'price': 45, 'image': 'danie2.jpg'},
        ],
        'Desery': [
            {'name': 'Deser 1', 'description': 'Opis deseru 1', 'price': 15, 'image': 'deser1.jpg'},
            {'name': 'Deser 2', 'description': 'Opis deseru 2', 'price': 18, 'image': 'deser2.jpg'},
        ],
    }
    return render_template('menu.html', menu_items=menu_items)

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']
        
        conn = get_db_connection()
        conn.execute('INSERT INTO users (username, password, role) VALUES (?, ?, ?)',
                     (username, password, role))
        conn.commit()
        conn.close()
        
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE username = ? AND password = ?', 
                            (username, password)).fetchone()
        conn.close()
        
        if user:
            session['logged_in'] = True
            session['username'] = user['username']
            session['role'] = user['role']
            session['user_id'] = user['id']
            return redirect(url_for('home'))
        else:
            return 'Invalid credentials'
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    session.clear()
    return redirect(url_for('home'))

@app.route('/customer', methods=['GET', 'POST'])
@login_required
def customer():
    conn = get_db_connection()
    if request.method == 'POST':
        if 'cart' in session:
            for item in session['cart']:
                conn.execute('INSERT INTO orders (user_id, item_name, item_description, item_price, quantity, status) VALUES (?, ?, ?, ?, ?, ?)',
                             (session['user_id'], item['name'], item['description'], item['price'], item['quantity'], 'Przyjęte'))
            conn.commit()
            session.pop('cart', None)
    
    orders = conn.execute('SELECT * FROM orders WHERE user_id = ?', (session['user_id'],)).fetchall()
    conn.close()
    return render_template('customer.html', orders=orders)

@app.route('/staff')
@login_required
@staff_required
def staff():
    conn = get_db_connection()
    orders = conn.execute('SELECT * FROM orders').fetchall()
    conn.close()
    return render_template('staff.html', orders=orders)

@app.route('/admin', methods=['GET', 'POST'])
@login_required
@admin_required
def admin():
    conn = get_db_connection()
    if request.method == 'POST':
        if 'delete' in request.form:
            order_id = request.form['order_id']
            conn.execute('DELETE FROM orders WHERE id = ?', (order_id,))
        elif 'update' in request.form:
            order_id = request.form['order_id']
            status = request.form['status']
            conn.execute('UPDATE orders SET status = ? WHERE id = ?', (status, order_id))
        conn.commit()
    
    orders = conn.execute('SELECT * FROM orders').fetchall()
    conn.close()
    return render_template('admin.html', orders=orders)

if __name__ == '__main__':
    app.run(debug=True)
