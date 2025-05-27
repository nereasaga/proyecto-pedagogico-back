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
        cur.execute(query, params or ())
        if commit:
            conn.commit()
        if fetch_one:
            try:
                return cur.fetchone()
            except psycopg2.ProgrammingError:
                # No hay resultados para fetch
                return None
        elif query.strip().upper().startswith("SELECT"):
            return cur.fetchall()
        else:
            return None
    except Exception as e:
        conn.rollback()
        print(f"Error en consulta: {e}")
        raise e
    finally:
        cur.close()
