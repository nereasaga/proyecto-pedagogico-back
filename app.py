# app.py
from flask import Flask, g
from dotenv import load_dotenv
from flask import render_template
from flask_jwt_extended import JWTManager
import os
from datetime import timedelta

load_dotenv()

app = Flask(__name__)
app.config.from_object('config.Config')

# Configuración de JWT
app.config["JWT_SECRET_KEY"] = app.config['SECRET_KEY']  # Usa la misma clave secreta
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=1)  # Tokens expiran en 1 hora
app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(days=30)  # Refresh tokens duran 30 días
app.config["JWT_TOKEN_LOCATION"] = ["headers"]  # Dónde buscar los tokens
app.config["JWT_HEADER_NAME"] = "Authorization"  # Nombre del header
app.config["JWT_HEADER_TYPE"] = "Bearer"  # Tipo de token en el header

jwt = JWTManager(app)

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
from auth import auth_bp

app.register_blueprint(empleados_bp)
app.register_blueprint(calendario_bp)
app.register_blueprint(auth_bp)

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
