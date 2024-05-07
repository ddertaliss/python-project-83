import os
import psycopg2
from dotenv import load_dotenv
from flask import Flask, render_template

app = Flask(__name__)
load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

conn = psycopg2.connect(DATABASE_URL)
cur = conn.cursor()

@app.route('/')
def start():
    cur.execute('SELECT * FROM users')
    # cur.execute('INSERT INTO users (name) VALUES ("meh")')
    all = cur.fetchall()
    print(all)
    cur.close()
    return 'test ^-^'

#if __name__ == '__main__':
#    start(app)
