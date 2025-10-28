# app.py
from flask import Flask
app = Flask(__name__)

@app.route('/')
def home():
    return "Chào mừng bạn đến với Hóng Hớt Đường Phố!"

if __name__ == '__main__':
    app.run()
