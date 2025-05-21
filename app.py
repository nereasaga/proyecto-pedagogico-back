from flask import Flask, g # Importamos 'g' para almacenar la conexión
import psycopg2
from dotenv import load_dotenv
import os

# Cargar variables de entorno del archivo .env
load_dotenv()

app = Flask(__name__)
app.config.from_object('config.Config')

# --- Gestión de la Conexión a la Base de Datos ---
def get_db_connection():
    """Establece una conexión a la base de datos PostgreSQL."""
    if 'db_conn' not in g:
        g.db_conn = psycopg2.connect(app.config['DATABASE_URL'])
    return g.db_conn

@app.teardown_appcontext
def close_db_connection(exception):
    """Cierra la conexión a la base de datos al finalizar la solicitud."""
    db_conn = g.pop('db_conn', None)
    if db_conn is not None:
        db_conn.close()
# --- Fin Gestión de la Conexión ---


# Importar las rutas (ahora no necesitamos importar modelos aquí, ya que las consultas se harán en las rutas)
from routes import *

if __name__ == '__main__':
    # No necesitamos db.create_all() ya que no usamos SQLAlchemy
    app.run(debug=True)