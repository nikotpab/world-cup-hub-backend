from flask import Flask, jsonify
from app.infrastructure.database import db
from app.config import DevelopmentConfig

def create_app(config_class=DevelopmentConfig):
    app = Flask(__name__)
    
    app.config.from_object(config_class)
    
    db.init_app(app)
    
    from app.presentation.api.user_api import user_bp
    from app.presentation.api.match_api import match_bp
    from app.presentation.api.ticket_api import ticket_bp
    from app.presentation.api.album_api import album_bp
    from app.presentation.api.betting_api import betting_bp
    from app.presentation.api.admin_api import admin_bp
    
    app.register_blueprint(user_bp, url_prefix='/api/v1')
    app.register_blueprint(match_bp, url_prefix='/api/v1')
    app.register_blueprint(ticket_bp, url_prefix='/api/v1')
    app.register_blueprint(album_bp, url_prefix='/api/v1')
    app.register_blueprint(betting_bp, url_prefix='/api/v1')
    app.register_blueprint(admin_bp, url_prefix='/api/v1')
    
    from sqlalchemy.exc import SQLAlchemyError
    
    @app.errorhandler(Exception)
    def handle_exception(e):
        from app.infrastructure.logger import app_logger
        
        if hasattr(e, 'status_code'):
             # Nuestros propios errores (Ej ValidationError o lógicos)
             return jsonify({"error": "ERR_VALIDATION", "message": str(e)}), e.status_code
             
        if isinstance(e, SQLAlchemyError):
             # Ocultar la estructura SQL real
             app_logger.error({"event":"db_error", "details": str(e)}) # Se saneará 
             return jsonify({"error": "ERR_DATABASE_COLLISION", "message": "Transaction could not be completed"}), 409
             
        # Errores no capturados
        app_logger.error({"event":"critical_uncaught_error", "details": str(e)})
        return jsonify({"error": "ERR_INTERNAL_SERVER", "message": "Unexpected platform error"}), 500
    
    return app
