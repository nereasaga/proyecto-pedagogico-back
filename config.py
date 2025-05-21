import os

class Config:
    # URL de la base de datos PostgreSQL
    DATABASE_URL = os.environ.get('DATABASE_URL') or \
                   'postgresql://postgres:111@localhost:5432/employeeCalendar'
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'una_clave_secreta_muy_segura_por_defecto'