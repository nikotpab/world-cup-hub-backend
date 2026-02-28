# config.py
import os

class Config:
    # Configuración base
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'clave-secreta-de-desarrollo'

class DevelopmentConfig(Config):
    DEBUG = True
    # Tu cadena de conexión a MySQL
    SQLALCHEMY_DATABASE_URI = "mysql+mysqldb://<user>:<pass>@<host>:<port>/<dbname>"

# Puedes tener otras para ProductionConfig o TestingConfig