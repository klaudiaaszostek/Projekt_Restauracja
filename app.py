from flask import Flask, render_template, redirect, url_for, request, session, flash
from functools import wraps
import sqlite3
import json

app = Flask(__name__)
app.secret_key = 'supersecretkey'

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            flash('Musisz być zalogowany, aby uzyskać dostęp do tej strony.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('role') != 'admin':
            flash('Nie masz uprawnień, aby uzyskać dostęp do tej strony.', 'danger')
            return redirect(url_for('home'))
        return f(*args, **kwargs)
    return decorated_function

def staff_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('role') not in ['admin', 'staff']:
            flash('Nie masz uprawnień, aby uzyskać dostęp do tej strony.', 'danger')
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
        item_image = request.form['item_image']

        cart_item = {
            'name': item_name,
            'description': item_description,
            'price': float(item_price),
            'quantity': item_quantity,
            'image': item_image
        }

        session['cart'].append(cart_item)
        session.modified = True
        flash('Dodano do koszyka: {} x{}'.format(item_name, item_quantity), 'success')
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
        
        flash('Rejestracja zakończona sukcesem. Możesz się teraz zalogować.', 'success')
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
            flash('Zalogowano pomyślnie.', 'success')
            return redirect(url_for('home'))
        else:
            flash('Nieprawidłowa nazwa użytkownika lub hasło.', 'danger')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    session.clear()
    flash('Wylogowano pomyślnie.', 'success')
    return redirect(url_for('home'))

@app.route('/customer', methods=['GET', 'POST'])
@login_required
def customer():
    conn = get_db_connection()
    if request.method == 'POST':
        if 'cart' in session:
            order_items = json.dumps(session['cart'])
            total_price = calculate_total_cost(session['cart'])
            conn.execute('INSERT INTO orders (user_id, order_items, total_price, status) VALUES (?, ?, ?, ?)',
                         (session['user_id'], order_items, total_price, 'Przyjęte'))
            conn.commit()
            session.pop('cart', None)
            flash('Zamówienie złożone pomyślnie.', 'success')
    
    orders = conn.execute('SELECT * FROM orders WHERE user_id = ?', (session['user_id'],)).fetchall()
    conn.close()
    return render_template('customer.html', orders=orders)

@app.route('/staff', methods=['GET', 'POST'])
@login_required
@staff_required
def staff():
    conn = get_db_connection()
    if request.method == 'POST':
        if 'update' in request.form:
            order_id = request.form['order_id']
            status = request.form['status']
            conn.execute('UPDATE orders SET status = ? WHERE id = ?', (status, order_id))
            flash('Status zamówienia został zaktualizowany.', 'success')
        conn.commit()
    
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
            flash('Zamówienie zostało usunięte.', 'success')
        elif 'update' in request.form:
            order_id = request.form['order_id']
            status = request.form['status']
            conn.execute('UPDATE orders SET status = ? WHERE id = ?', (status, order_id))
            flash('Status zamówienia został zaktualizowany.', 'success')
        elif 'edit' in request.form:
            order_id = request.form['order_id']
            order_items = []
            for item_name, item_quantity, item_price in zip(request.form.getlist('item_name'), request.form.getlist('item_quantity'), request.form.getlist('item_price')):
                if item_name and item_quantity and item_price:
                    order_items.append({
                        'name': item_name,
                        'quantity': int(item_quantity),
                        'price': float(item_price)
                    })
            total_price = sum(item['price'] * item['quantity'] for item in order_items)
            conn.execute('UPDATE orders SET order_items = ?, total_price = ? WHERE id = ?', 
                         (json.dumps(order_items), total_price, order_id))
            flash('Zamówienie zostało zaktualizowane.', 'success')
        conn.commit()
    
    orders = conn.execute('SELECT * FROM orders').fetchall()
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
    conn.close()
    return render_template('admin.html', orders=orders, menu=menu_items)

def calculate_total_cost(cart):
    return sum(item['price'] * item['quantity'] for item in cart)

@app.context_processor
def utility_processor():
    return dict(calculate_total_cost=calculate_total_cost)

@app.template_filter('fromjson')
def fromjson(value):
    return json.loads(value)

if __name__ == '__main__':
    app.run(debug=True)
