# db.py
import psycopg2
from flask import g, current_app

def get_db_connection():
    if 'db_conn' not in g:
        g.db_conn = psycopg2.connect(current_app.config['DATABASE_URL'])
    return g.db_conn

def execute_query(query, params=None, fetch_one=False, fetch_all=False, commit=False):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute(query, params)

        result = None
        if fetch_one:
            result = cur.fetchone()
        elif fetch_all:
            result = cur.fetchall()

        if commit:
            conn.commit()

        return result
    except Exception as e:
        conn.rollback()
        print(f"Error en consulta: {e}")
        raise e
    finally:
        cur.close()
