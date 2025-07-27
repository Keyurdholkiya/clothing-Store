from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_session import Session
import requests
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config["SECRET_KEY"] = "your-secret-key-here"
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Fake database for demonstration
users = {}
products = []
cart = {}

# Load products from FakeStoreAPI
def load_products():
    global products
    response = requests.get('https://fakestoreapi.com/products')
    products = response.json()

load_products()

# @app.route("/")
# def index():
#     search_query = request.args.get('search', '')
#     filtered_products = [p for p in products if search_query.lower() in p['title'].lower() or 
#                          search_query.lower() in p['description'].lower() or 
#                          search_query.lower() in p['category'].lower()]
    
#     cart_items = session.get('cart', {})
#     cart_count = sum(cart_items.values())
#     cart_total = sum(products[next((i for i, p in enumerate(products) if p['id'] == int(id)))]['price'] * qty 
#                    for id, qty in cart_items.items())
    
#     return render_template('store.html', 
#                          products=filtered_products if search_query else products,
#                          search_query=search_query,
#                          cart_count=cart_count,
#                          cart_total=round(cart_total, 2))

@app.route("/add_to_cart/<int:product_id>")
def add_to_cart(product_id):
    if 'cart' not in session:
        session['cart'] = {}
    
    cart = session['cart']
    cart[str(product_id)] = cart.get(str(product_id), 0) + 1
    session['cart'] = cart
    
    flash('Item added to cart!', 'success')
    return redirect(url_for('index'))

# @app.route("/remove_from_cart/<int:product_id>")
# def remove_from_cart(product_id):
#     if 'cart' not in session:
#         return redirect(url_for('index'))
    
#     cart = session['cart']
#     if str(product_id) in cart:
#         if cart[str(product_id)] > 1:
#             cart[str(product_id)] -= 1
#         else:
#             del cart[str(product_id)]
#         session['cart'] = cart
#         flash('Item removed from cart!', 'info')
    
#     return redirect(url_for('index'))

# @app.route("/checkout")
# def checkout():
#     if 'username' not in session:
#         flash('Please login to checkout', 'warning')
#         return redirect(url_for('login'))
    
#     cart_items = session.get('cart', {})
#     if not cart_items:
#         flash('Your cart is empty!', 'warning')
#         return redirect(url_for('index'))
    
#     # Process payment here (simulated)
#     session['cart'] = {}
#     flash('Order placed successfully!', 'success')
#     return redirect(url_for('index'))
@app.route("/")
def index():
     return render_template('store.html',
                         products= products)

@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if username in users and check_password_hash(users[username]['password'], password):
            session['username'] = username
            flash('Logged in successfully!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password', 'danger')
    
    return render_template('login.html')

@app.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        
        if username in users:
            flash('Username already exists', 'danger')
        else:
            users[username] = {
                'password': generate_password_hash(password),
                'email': email
            }
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route("/logout")
def logout():
    session.pop('username', None)
    flash('Logged out successfully', 'info')
    return redirect(url_for('index'))

@app.route("/account")
def account():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    return render_template('account.html', user=users.get(session['username']))

if __name__ == '__main__':
    app.run(debug=True)