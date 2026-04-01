from flask import Flask
from .database import db
from config import DevelopmentConfig

def create_app(config_class=DevelopmentConfig):
    app = Flask(__name__)
    
    app.config.from_object(config_class)
    
    db.init_app(app)
    
    return app