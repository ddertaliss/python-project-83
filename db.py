from dotenv import load_dotenv
from datetime import datetime
from bs4 import BeautifulSoup
import psycopg2
import os

load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')


def get_url_info():
    with psycopg2.connect(DATABASE_URL) as con:
        with con.cursor() as cur:
            cur.execute('''
                SELECT id, name,
                DATE(created_at)
                FROM urls
                ORDER BY id
                DESC
            ''')
            return cur.fetchall()


def get_url_check():
    with psycopg2.connect(DATABASE_URL) as con:
        with con.cursor() as cur:
            cur.execute('''
                SELECT url_id,
                status_code
                FROM url_checks
                WHERE id IN
                (SELECT MAX(id)
                FROM url_checks
                GROUP BY url_id)
            ''')
            return cur.fetchall()


def get_dublicates(item):
    with psycopg2.connect(DATABASE_URL) as con:
        with con.cursor() as cur:
            cur.execute('SELECT * FROM urls WHERE name = %s', (item, ))
            return cur.fetchall()


def if_no_duplicates(name, created_at):
    with psycopg2.connect(DATABASE_URL) as con:
        with con.cursor() as cur:
            cur.execute('''
                        INSERT INTO urls (name, created_at) VALUES (%s, %s)''',
                        (name, created_at)
                        )
            con.commit()


def get_id(name):
    with psycopg2.connect(DATABASE_URL) as con:
        with con.cursor() as cur:
            cur.execute('''
                        SELECT id
                        FROM urls
                        WHERE name = %s
                        ''',
                        (name, )
                        )
            return cur.fetchall()


def get_temp_table_info_show(id):
    with psycopg2.connect(DATABASE_URL) as con:
        with con.cursor() as cur:
            cur.execute('''
                        SELECT id, name,
                        DATE(created_at)
                        FROM urls
                        WHERE id = %s
                        ''',
                        (id,)
                        )
            return cur.fetchall()


def get_check_info_show(id):
    with psycopg2.connect(DATABASE_URL) as con:
        with con.cursor() as cur:
            cur.execute('''
                        SELECT id, status_code,
                        h1, title,
                        description,
                        DATE(created_at)
                        FROM url_checks
                        WHERE url_id = %s
                        ORDER BY id
                        DESC
                        ''',
                        (id,)
                        )
            return cur.fetchall()


def get_site_name_checks(id):
    with psycopg2.connect(DATABASE_URL) as con:
        with con.cursor() as cur:
            cur.execute('''
                        SELECT name
                        FROM urls
                        WHERE id = %s''',
                        (id,)
                        )
            return cur.fetchall()


def check_site(id, req, response):
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

    with psycopg2.connect(DATABASE_URL) as con:
        with con.cursor() as cur:
            cur.execute('''
                        INSERT INTO url_checks (
                            url_id, status_code,
                            h1, title,
                            description, created_at
                            )
                        VALUES (%s, %s, %s, %s, %s, %s)''',
                        (
                            id, int(response),
                            str(h1_text), str(title_text),
                            str(meta_text), datetime.now(),
                        )
                        )
            con.commit()
            return True
