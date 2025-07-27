import os
import uuid
import requests
import base64
from werkzeug.utils import secure_filename
from PIL import Image
from io import BytesIO
from flask_session import Session
from flask import Flask , render_template , request , redirect, session, url_for

app = Flask(__name__)
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config["SECRET_KEY"] = "your-secret-key-here"
app.config["SESSION_TYPE"] = "filesystem"
Session(app)
# with open("data.json","r") as f:
#     reson_json = f.read()
url = 'https://fakestoreapi.com/products'
response = requests.get(url)
reson_json = response.json()
registers = {}
addresses = {}
order = []
add = []
@app.route("/")
def index():
    if "username" not in session:
        session['username'] = ""

    return render_template('new.html' , reson_json = reson_json)

@app.route("/women")
def women():
    women_products = [p for p in reson_json if p['category'] == "women's clothing"]
    return render_template('new.html', reson_json=women_products)

@app.route("/men")
def men():
    men_products = [p for p in reson_json if p['category'] == "men's clothing"]
    return render_template('new.html', reson_json=men_products)

@app.route("/kids")
def kids():
    kids_products = [p for p in reson_json if p['category'] in ["electronics", "jewelery"]]  # Adjust as needed
    return render_template('new.html', reson_json=kids_products)
@app.route("/register",methods = ["GET","POST"])
def register():
    if request.method =="POST":
        user_name = request.form["username"]
        user_pass = request.form["password"]
        email = request.form["email"]
        if user_name in registers:
            print("already exixst")
        else:
            registers[user_name] = {"user_password":user_pass,"email":email}
            print(registers)
        return redirect(url_for('login'))  #enter the funcation name
    return render_template("register.html")



@app.route("/login",methods = ["GET","POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        print(registers)
        if username in registers and password == registers[username]["user_password"]:
            session['username'] = username
            print("succusees..!!!")
            return redirect(url_for('index'))
        else:
            return redirect(url_for('register'))
    return render_template('login.html')

@app.route("/account")
def account():
    datas = []
    if "username" not in session:
        return redirect(url_for("login"))  # ✅ Fixed: missing return
    
    if 'order_items' in session:
        datas = session.get('order_items')

    print(add)  # This will now show individual address dicts
    for i in add:
        print(i['name'])
    return render_template("account.html",
                           user=registers.get(session["username"]),
                           datas=datas,
                           addresses=add)  
@app.route("/logout")
def logout():
    session.pop('username',None)
    return redirect(url_for('index'))

@app.route("/address", methods=["GET", "POST"])
def address():
    if request.method == "POST":
        street = request.form["street"]
        city = request.form["city"]
        Province = request.form["Province"]
        code = request.form["code"]
        coutry = request.form["coutry"]
        phone = request.form["phone"]
        first = request.form["first"]
        last = request.form["last"]
        name = f"{first}  {last}"

        if name in addresses:
            print("Address already exists")
        else:
            addresses[name] = {
                "street": street,
                "city": city,
                "Province": Province,
                "code": code,
                "coutry": coutry,
                "phone": phone,
                "name": name
            }

            # ✅ Append only the new address
            add.append(addresses[name].copy())
        
        return redirect(url_for('account'))

    return render_template("address.html")

@app.route("/remove/<address_key>")
def remove(address_key):
    # Remove from addresses dictionary
    if address_key in addresses:
        del addresses[address_key]

    # Remove from add list where name matches
    global add
    add = [addr for addr in add if addr.get("name") != address_key]

    return redirect(url_for('account'))

@app.route("/add_to_cart/<int:product_id>")
def add_to_cart(product_id):
    # Initialize cart if not present
    if 'cart' not in session:
        session['cart'] = []

    # Add item to cart only if not already in cart
    if product_id not in session['cart']:
        session['cart'].append(product_id)
        session.modified = True  # Mark session as changed

    return redirect(url_for('cart'))  # Redirect to home or product page
@app.route("/cart")
def cart():
    if 'cart' not in session or not session['cart']:
        return render_template("cart.html", items=[], total=0, address=None)

    # Get only items in cart important
    cart_items = [item for item in reson_json if item["id"] in session['cart']]
    # print("cart_items :=",cart_items)
    # print(cart_items.get("id"))
    
    # Calculate total
    total = sum(item["price"] for item in cart_items)

    # Get first address as default
    address = next(iter(addresses.values()), None)

    return render_template("cart.html", items=cart_items, total=total, address=address,order_id = str(uuid.uuid4()))
@app.route("/remove_from_cart/<int:product_id>")
def remove_from_cart(product_id):
    if 'cart' in session and product_id in session['cart']:
        session['cart'].remove(product_id)
        session.modified = True
    return redirect(url_for('cart'))


@app.route('/place_order', methods=['POST'])
def place_order():
    global order
    product_ids = request.form.get('product_ids')  # Convert "1,2,3" to ['1', '2', '3']
    product_ids = [int(id) for id in product_ids.split(',')] #[1,2,3]
    for i in product_ids:
        print("i := ",i)
        order.append(i)
    # print("order:=",order)
    items = [item for item in reson_json if item["id"] in order]
    # print(items)
    # Process the order for all items
    if 'order_items' not in session:
        session['order_items'] = []
    if items not in session['order_items']:
        session['order_items'] = items
    if 'cart' in session:
        session['cart'] = []
        
    return redirect(url_for('account'))

@app.route("/order_history")
def order_history():
    global order
    if 'order_items' in session:
        session['order_items'] = []
        order = []
    return redirect(url_for('account'))


# Configure upload folder
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload_avatar', methods=['POST'])
def upload_avatar():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    if 'avatar' not in request.files:
        print('No file selected')
        return redirect(url_for('account'))
    
    file = request.files['avatar']
    if file.filename == '':
        print('No file selected')
        return redirect(url_for('account'))
    
    if file and allowed_file(file.filename):
        filename = secure_filename(f"{session['username']}.{file.filename.rsplit('.', 1)[1].lower()}")
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Store the path in user's data
        if session['username'] in registers:
            registers[session['username']]['avatar'] = filename
        
        print('Avatar updated successfully!')
    
    return redirect(url_for('account'))

app.run(debug=True)

