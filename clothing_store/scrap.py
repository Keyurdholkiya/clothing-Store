import requests
import base64
from PIL import Image
from io import BytesIO
from flask import Flask , render_template 

app = Flask(__name__)
url = 'https://fakestoreapi.com/products'

@app.route("/")
def index():
    response = requests.get(url)
    reson_json = response.json()
    return render_template('index.html' , reson_json = reson_json)

app.run(debug=True)
