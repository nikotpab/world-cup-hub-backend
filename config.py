import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'clave-secreta-de-desarrollo'
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY')


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = "mysql+mysqldb://<user>:<pass>@<host>:<port>/<dbname>"