import os
from datetime import timedelta

class Config:
    # URL de la base de datos PostgreSQL
    DATABASE_URL = os.environ.get('DATABASE_URL') or \
                    'postgresql://allan:1234@192.168.21.110:5432/proyecto_pedagogico'
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'prueba'
    
    # Configuraciones JWT
    JWT_SECRET_KEY = SECRET_KEY
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
