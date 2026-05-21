from flask import Flask, jsonify
from flask_cors import CORS
from app.infrastructure.database import db
from app.config import get_config

def _run_startup_migrations(app):
    """Añade columnas nuevas al esquema en un hilo para no bloquear el arranque del worker."""
    import threading, time

    def _migrate():
        time.sleep(5)  # espera a que el worker esté listo para recibir requests
        with app.app_context():
            try:
                from app.infrastructure.database import db
                db.session.execute(db.text(
                    'ALTER TABLE "USER" ADD COLUMN IF NOT EXISTS preferences JSONB DEFAULT \'{}\'::jsonb'
                ))
                db.session.execute(db.text(
                    "ALTER TABLE trade_proposal ADD COLUMN IF NOT EXISTS offered_sticker_ids JSONB DEFAULT '[]'::jsonb"
                ))
                # Migrate existing rows: copy offered_sticker_id → offered_sticker_ids
                db.session.execute(db.text("""
                    UPDATE trade_proposal
                    SET offered_sticker_ids = jsonb_build_array(offered_sticker_id)
                    WHERE offered_sticker_id IS NOT NULL
                      AND (offered_sticker_ids IS NULL
                           OR offered_sticker_ids = '[]'::jsonb
                           OR jsonb_array_length(offered_sticker_ids) = 0)
                """))
                db.session.commit()
            except Exception:
                db.session.rollback()

    t = threading.Thread(target=_migrate, daemon=True, name="startup-migrations")
    t.start()



def _start_ttl_worker(app):
    """Hilo daemon que libera reservas expiradas cada 60 s."""
    import threading, time
    from app.infrastructure.logger import app_logger

    def _run():
        time.sleep(10)  # espera inicial para que el servidor arranque
        while True:
            try:
                with app.app_context():
                    from app.application.services.ticket_service import TicketService
                    from app.infrastructure.repositories.ticket_repository import SqlAlchemyTicketRepository
                    result = TicketService(SqlAlchemyTicketRepository()).expire_reservations()
                    if result.get("expired", 0) > 0:
                        app_logger.info({"event": "ttl_worker_ran", "expired": result["expired"]})
            except Exception:
                pass  # No romper el hilo por errores transitorios de BD
            time.sleep(60)

    t = threading.Thread(target=_run, daemon=True, name="ttl-worker")
    t.start()


_API_V1 = '/api/v1'


def create_app(config_class=None):
    import os
    app = Flask(__name__)
    allowed_origins = os.environ.get('CORS_ORIGINS', '*')
    CORS(app, origins=allowed_origins.split(',') if allowed_origins != '*' else '*')

    app.config.from_object(config_class or get_config())
    
    db.init_app(app)
    
    from app.presentation.api.user_api import user_bp
    from app.presentation.api.match_api import match_bp
    from app.presentation.api.ticket_api import ticket_bp
    from app.presentation.api.album_api import album_bp
    from app.presentation.api.community_api import community_bp
    from app.presentation.api.bet_api import bet_bp
    from app.presentation.api.admin_api import admin_bp
    from app.presentation.api.auth_api import auth_bp
    from app.presentation.api.sports_bet_api import sports_bet_bp
    from app.presentation.api.proxy_api import proxy_bp
    from app.presentation.api.news_api import news_bp
    from app.presentation.api.feed_api import feed_bp

    app.register_blueprint(user_bp, url_prefix=_API_V1)
    app.register_blueprint(match_bp, url_prefix=_API_V1)
    app.register_blueprint(ticket_bp, url_prefix=_API_V1)
    app.register_blueprint(album_bp, url_prefix=_API_V1)
    app.register_blueprint(community_bp, url_prefix=_API_V1)
    app.register_blueprint(bet_bp, url_prefix=_API_V1)
    app.register_blueprint(admin_bp, url_prefix=_API_V1)
    app.register_blueprint(auth_bp, url_prefix=_API_V1)
    app.register_blueprint(sports_bet_bp, url_prefix=_API_V1)
    app.register_blueprint(proxy_bp, url_prefix=_API_V1)
    app.register_blueprint(news_bp, url_prefix=_API_V1)
    app.register_blueprint(feed_bp, url_prefix=_API_V1)

    @app.route('/api/v1/health', methods=['GET'])
    def health_check():
        return jsonify({'status': 'ok'}), 200
    
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
    
    _run_startup_migrations(app)
    _start_ttl_worker(app)
    # Daily pack distribution runs as an AWS Lambda (lambda_daily_packs.py)
    # triggered by EventBridge at 05:00 UTC (00:00 UTC-5). Not started here.
    return app
