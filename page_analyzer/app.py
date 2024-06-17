import os
import psycopg2
import requests
from dotenv import load_dotenv
from flask import Flask, render_template, request, flash, redirect, url_for 
from urllib.parse import urlparse
from validators.url import url
from datetime import datetime

app = Flask(__name__)
load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

conn = psycopg2.connect(DATABASE_URL)
cur = conn.cursor()

@app.route('/', methods=['GET'])
def start():
    return render_template('home.html')


@app.route('/urls', methods=['POST', 'GET'])
def show():
    flag = False
    if request.method == 'GET':
        cur.execute('SELECT * FROM urls')
        info = cur.fetchall()
        return render_template('show.html', info=info)
    if request.method == 'POST':
        site_url = request.form.get('url')
        if url:
            print('юрл есть')
            if len(site_url) > 255:
                print('длинный сайт')
                flash('too long', 'err')
            else:
                print('длина нормальная')
                print('переходим в иф')
                if url(site_url):
                    print("юрл валидатор прошел")
                    print(site_url)
                    print('арывоаывр')
                    flag = True
                    print('флаг изменен на true')
                else:
                    print('ошибка в трае')
                    flash('unable to load site')
        if flag:
            print('флаг true, продолжаем')
            site = urlparse(site_url)
            print('юрл парс')
            print(site)
            print(site.scheme)
            print(site.hostname)
            full_name = site.scheme + '://' + site.hostname
            print('full name:', full_name)
            cur.execute("SELECT * FROM urls WHERE name = %s", (full_name, ))
            dublicates = cur.fetchall()
            print('GOOOFY AHH DUBLICATE:', dublicates)
            if len(dublicates) < 1:
                print('записи еще нет, добавляем в таблицу')
                cur.execute("INSERT INTO urls (name, created_at) VALUES (%s, %s)", (full_name, datetime.now()))
                conn.commit()
            else:  # потом удалить
                flash('Запись уже добавлена', 'ok')
                print('обнаржены дубликаты, запись не добавлена')  # удалить
            cur.execute('SELECT * FROM urls ORDER BY created_at')
            info = cur.fetchall()
            print('инфо с таблицы:', info)
            print('modified:', info)
            cur.execute('SELECT id FROM urls WHERE name = %s', (full_name, ))
            id = cur.fetchall()
            id = id[0][0]
            print('ID:', id)
            return redirect(url_for('.show_id', id=id))

@app.route('/urls/<int:id>')
def show_id(id):
    cur.execute("SELECT * FROM urls WHERE id = %s", (id,))
    info = cur.fetchall()
    return render_template('checks.html', info=info, id=id) 

@app.post('/urls/<id>/checks')
def checks(id):
    cur.execute("INSERT INTO url_checks (url_id) VALUES (%s)", (id,))
    conn.commit()
    cur.execute('SELECT * FROM url_checks WHERE url_id = %s', (id,))
    info = cur.fetchall()
    return render_template('checks.html', info=info, id=id)
    