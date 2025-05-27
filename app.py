from flask import Flask, g
from dotenv import load_dotenv
from flask import render_template
import os
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from datetime import timedelta

load_dotenv()

app = Flask(__name__)
app.config.from_object('config.Config')
CORS(app)

# Configuración de JWT
app.config["JWT_SECRET_KEY"] = app.config['SECRET_KEY']
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=1)
app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(days=30)
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
from calendario.routes import festivos_bp
from calendario.horarios_routes import horarios_bp
from calendario.routes import roles_bp
from calendario.routes import centros_bp
from auth import auth_bp  # Importar el blueprint de autenticación
from calendario.vacaciones_routes import vacaciones_bp
from calendario.routes import tipos_festivo_bp 


app.register_blueprint(empleados_bp)
app.register_blueprint(calendario_bp)
app.register_blueprint(festivos_bp)
app.register_blueprint(horarios_bp)
app.register_blueprint(roles_bp)
app.register_blueprint(centros_bp)
app.register_blueprint(auth_bp)  # Registrar el blueprint de autenticación
app.register_blueprint(vacaciones_bp)
app.register_blueprint(tipos_festivo_bp)




@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
