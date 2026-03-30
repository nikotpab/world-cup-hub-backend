from flask import Flask
from .database import db
from config import DevelopmentConfig

def create_app():
    app = Flask(__name__)
    
    app.config.from_object(DevelopmentConfig)
    
    db.init_app(app)
    
    return app