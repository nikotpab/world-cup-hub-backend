from flask import Flask, jsonify
from .database import db
from config import DevelopmentConfig

def create_app(config_class=DevelopmentConfig):
    app = Flask(__name__)
    
    app.config.from_object(config_class)
    
    db.init_app(app)
    
    @app.errorhandler(Exception)
    def handle_exception(e):
        if hasattr(e, 'status_code'):
            return jsonify({"error": str(e)}), e.status_code
        # Captura errores genéricos que no maneja la capa de servicios
        return jsonify({"error": "Internal Server Error", "message": str(e)}), 500
    
    return app