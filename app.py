from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/menu')
def menu():
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

if __name__ == '__main__':
    app.run(debug=True)
