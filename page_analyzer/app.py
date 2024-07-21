import os
import requests
from dotenv import load_dotenv
from flask import Flask, render_template, request, flash, redirect, url_for
from urllib.parse import urlparse
from validators.url import url
from datetime import datetime
import db

app = Flask(__name__)
load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')


@app.route('/', methods=['GET'])
def start():
    return render_template('home.html')


@app.route('/urls', methods=['POST', 'GET'])
def show():
    flag = False
    if request.method == 'GET':
        urls_info = db.get_url_info()
        urls_check = db.get_url_check()
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
        return render_template('show.html', info=info)

    if request.method == 'POST':
        site_url = request.form.get('url')
        if url:
            print('юрл есть')
            if len(site_url) > 255:
                print('длинный сайт')
                flash('Некорректный URL')
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
                    flash('Некорректный URL')
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
            dublicates = db.get_dublicates(full_name)
            print('GOOOFY AHH DUBLICATE:', dublicates)
            if len(dublicates) < 1:
                print('записи еще нет, добавляем в таблицу')
                flash('Страница успешно добавлена')
                db.if_no_duplicates(full_name, datetime.now())
            else:  # потом удалить
                flash('Страница уже существует')
                print('обнаржены дубликаты, запись не добавлена')  # удалить
            id = db.get_id(full_name)
            id = id[0][0]
            print('ID:', id)
            return redirect(url_for('.show_id', id=id))


@app.route('/urls/<int:id>')
def show_id(id):
    temp_info = db.get_temp_table_info_show(id)
    print('table info', temp_info)
    table_info = {
        'id': temp_info[0][0],
        'name': temp_info[0][1],
        'created_at': temp_info[0][2]
    }
    print(table_info)
    check_info = db.get_check_info_show(id)
    return render_template(
        'checks.html',
        table_info=table_info,
        check_info=check_info,
        id=id
    )


@app.post('/urls/<id>/checks')
def checks(id):
    site_name = (db.get_site_name_checks(id))[0][0]
    req = requests.get(site_name)
    response = req.status_code
    if response != 200:
        flash('Произошла ошибка при проверке', 'error')
    else:
        if db.check_site(id, req, response):
            flash('Страница успешно проверена')
    return redirect(url_for('.show_id', id=id))
