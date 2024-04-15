from flask import Flask


app = Flask(__name__)

@app.route('/')
def start():
    return 'mhe)'

if __name__ == '__main__':
    start(app)
