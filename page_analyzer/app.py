from flask import Flask, render_template
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

@app.route('/')
def start():
    return render_template('home.html')

if __name__ == '__main__':
    start(app)
