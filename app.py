# app.py
from flask import Flask, g
from dotenv import load_dotenv
from flask import render_template
import os

load_dotenv()

app = Flask(__name__)
app.config.from_object('config.Config')

# Cierra conexión al final de la request
@app.teardown_appcontext
def close_db_connection(exception):
    from db import g  # Flask's global context
    db_conn = g.pop('db_conn', None)
    if db_conn:
        db_conn.close()

# Importa y registra blueprints
from empleados.routes import empleados_bp
from calendario.routes import calendario_bp

app.register_blueprint(empleados_bp)
app.register_blueprint(calendario_bp)

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
