import os
import psycopg2
import requests
from dotenv import load_dotenv
from flask import Flask, render_template, request, flash, redirect, url_for
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from validators.url import url
from datetime import datetime

app = Flask(__name__)
load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')


@app.route('/', methods=['GET'])
def start():
    return render_template('home.html')


@app.route('/urls', methods=['POST', 'GET'])
def show():
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    flag = False
    if request.method == 'GET':
        cur.execute(
            'SELECT id, name, DATE(created_at) FROM urls ORDER BY id DESC'
            )
        urls_info = cur.fetchall()
        cur.execute(
            'SELECT url_id, status_code FROM url_checks WHERE id IN (SELECT MAX(id) FROM url_checks GROUP BY url_id)'  # noqa: E501
            )
        urls_check = cur.fetchall()
        info = []

        for item in urls_info:
            info.append(
                {
                    'id': item[0],
                    'name': item[1],
                    'created_at': item[2],
                    'status_code': None
                    }
                )

        print(info)

        for indx, item in enumerate(info):
            id = item['id']
            print(id)
            for i in urls_check:
                if i[0] == id:
                    info[indx]['status_code'] = i[1]
        print(info)
        cur.close()
        conn.close()
        return render_template('show.html', info=info)

    if request.method == 'POST':
        cur = conn.cursor()
        site_url = request.form.get('url')
        if url:
            print('юрл есть')
            if len(site_url) > 255:
                print('длинный сайт')
                flash('Некорректый URL')
                return render_template('home.html'), 422
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
                    print('сайт не работает')
                    flash('Некорректый URL')
                    cur.close()
                    conn.close()
                    return render_template('home.html'), 422
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
                flash('Страница успешно добавлена')
                cur.execute(
                    "INSERT INTO urls (name, created_at) VALUES (%s, %s)",
                    (full_name, datetime.now())
                    )
                conn.commit()
            else:  # потом удалить
                flash('Страница уже существует')
                print('обнаржены дубликаты, запись не добавлена')  # удалить
            cur.execute('SELECT * FROM urls ORDER BY created_at')
            info = cur.fetchall()
            print('инфо с таблицы:', info)
            print('modified:', info)
            cur.execute('SELECT id FROM urls WHERE name = %s', (full_name, ))
            id = cur.fetchall()
            id = id[0][0]
            print('ID:', id)
            cur.close()
            conn.close()
            return redirect(url_for('.show_id', id=id))


@app.route('/urls/<int:id>')
def show_id(id):
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    cur.execute(
        'SELECT id, name, DATE(created_at) FROM urls WHERE id = %s', (id,)
        )
    temp_info = cur.fetchall()
    print('table info', temp_info)
    table_info = {
        'id': temp_info[0][0],
        'name': temp_info[0][1],
        'created_at': temp_info[0][2]
    }
    print(table_info)
    cur.execute('SELECT id, status_code, h1, title, description, DATE(created_at) FROM url_checks WHERE url_id = %s ORDER BY id DESC', (id,))  # noqa: E501
    check_info = cur.fetchall()
    cur.close()
    conn.close()
    return render_template(
        'checks.html',
        table_info=table_info,
        check_info=check_info,
        id=id
        )


@app.post('/urls/<id>/checks')
def checks(id):
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    cur.execute("SELECT name FROM urls WHERE id = %s", (id,))
    site_name = (cur.fetchall())[0][0]
    req = requests.get(site_name)
    response = req.status_code
    if response != 200:
        flash('Произошла ошибка при проверке', 'error')
    else:
        h1_text = ''
        title_text = ''
        meta_text = ''
        html = req.text
        soup = BeautifulSoup(html, 'html.parser')
        h1 = soup.h1
        print('h1:', h1)
        if h1 and h1.contents:
            h1_text = (h1.contents)[0]
        title = soup.title
        print('title:', title)
        if title and title.contents:
            title_text = (title.contents)[0]
        meta = soup(name='meta', attrs={'name': 'description'})
        print('meta:', meta)
        if meta and meta[0].get('content'):
            meta_text = meta[0].get('content')
        cur.execute(
            "INSERT INTO url_checks (url_id, status_code, h1, title, description, created_at) VALUES (%s, %s, %s, %s, %s, %s)",  # noqa E:501
            (id, int(response), str(h1_text), str(title_text), str(meta_text), datetime.now(),)  # noqa E:501
            )
        conn.commit()
        flash('Страница успешно проверена')
    cur.close()
    conn.close()
    return redirect(url_for('.show_id', id=id))
