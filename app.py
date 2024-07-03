import os
from flask import Flask, render_template, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from forms import LoginForm, RegisterForm, DishForm, MenuOrderForm, DishOrderForm
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['UPLOAD_FOLDER'] = 'uploads/'
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    role = db.Column(db.String(50), nullable=False)

class Dish(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), unique=True, nullable=False)
    price = db.Column(db.Float, nullable=False)
    foto = db.Column(db.String(255), nullable=False)

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    total_price = db.Column(db.Float, nullable=False)
    items = db.relationship('OrderItem', backref='order', lazy=True)

class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    dish_id = db.Column(db.Integer, db.ForeignKey('dish.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    dish = db.relationship('Dish', lazy=True)

@app.route('/', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data, method='pbkdf2')
        new_user = User(username=form.username.data, password=hashed_password, role=form.role.data)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            return redirect(url_for('menu'))
        flash('Invalid username or password')
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/menu', methods=['GET', 'POST'])
@login_required
def menu():
    form = MenuOrderForm()
    dishes = Dish.query.all()
    
    # Populate form with dishes
    if not form.dishes:
        for dish in dishes:
            form.dishes.append_entry({'dish_id': dish.id})
    
    if form.validate_on_submit():
        print("Form is validated")
        order = Order(user_id=current_user.id, total_price=0)
        db.session.add(order)
        db.session.commit()

        total_price = 0
        for dish_form in form.dishes.data:
            dish = Dish.query.get(dish_form['dish_id'])
            quantity = dish_form['quantity']
            if quantity >= 0:
                total_price += dish.price * quantity
                order_item = OrderItem(order_id=order.id, dish_id=dish.id, quantity=quantity)
                db.session.add(order_item)

        order.total_price = total_price
        db.session.commit()

        return redirect(url_for('summary', order_id=order.id))
    
    if form.errors:
        print("Form errors:", form.errors)

    dish_data = list(zip(form.dishes, dishes))
    return render_template('menu.html', form=form, dish_data=dish_data)

@app.route('/summary/<int:order_id>')
@login_required
def summary(order_id):
    order = Order.query.get_or_404(order_id)
    if order.user_id != current_user.id:
        flash('To nie twoje zamówienie.')
        return redirect(url_for('menu'))
    
    return render_template('summary.html', order=order)

@app.route('/add', methods=['GET', 'POST'])
@login_required
def add_dish():
    form = DishForm()
    if form.validate_on_submit():
        file = form.foto.data
        filename = file.filename
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        new_dish = Dish(name=form.name.data, price=form.price.data, foto=filepath)
        db.session.add(new_dish)
        db.session.commit()
        
        return redirect(url_for('menu'))
    return render_template('add.html', form=form)

if __name__ == '__main__':
    app.config['DEBUG'] = True
    with app.app_context():
        db.create_all()
        app.run(port=8000, debug=True)