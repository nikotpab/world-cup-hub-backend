import logging
from flask import Blueprint, request, jsonify, current_app
from app.application.services.auth_service import AuthService, _UnverifiedError

_log = logging.getLogger(__name__)
from app.infrastructure.repositories.user_repository import SqlAlchemyUserRepository

auth_bp = Blueprint('auth_bp', __name__)

user_repo = SqlAlchemyUserRepository()
auth_service = AuthService(user_repo)

@auth_bp.route('/auth/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        result = auth_service.register(data)
        return jsonify(result), 201
    except ValueError as e:
        return jsonify({"error": "ERR_BAD_REQUEST", "message": str(e)}), 400

@auth_bp.route('/auth/verify', methods=['POST'])
def verify():
    try:
        data = request.get_json()
        result = auth_service.verify_email(data)
        return jsonify(result), 200
    except ValueError as e:
        return jsonify({"error": "ERR_BAD_REQUEST", "message": str(e)}), 400

@auth_bp.route('/auth/resend', methods=['POST'])
def resend_verification():
    try:
        data = request.get_json()
        result = auth_service.resend_verification(data)
        return jsonify(result), 200
    except ValueError as e:
        return jsonify({"error": "ERR_BAD_REQUEST", "message": str(e)}), 400

@auth_bp.route('/auth/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        result = auth_service.login(data)
        return jsonify(result), 200
    except _UnverifiedError as e:
        return jsonify({"error": "ERR_UNVERIFIED", "message": str(e), "email": e.email}), 401
    except ValueError as e:
        return jsonify({"error": "ERR_UNAUTHORIZED", "message": str(e)}), 401

@auth_bp.route('/auth/logout', methods=['POST'])
def logout():
    """Revokes the JWT by blacklisting its jti in Redis."""
    auth_header = request.headers.get('Authorization', '')
    token = auth_header.removeprefix('Bearer ').strip()
    if token:
        try:
            import jwt as _jwt
            from app.infrastructure.cache.redis_client import redis_client
            secret_key = current_app.config.get('JWT_SECRET_KEY') or current_app.config.get('SECRET_KEY')
            payload = _jwt.decode(token, secret_key, algorithms=['HS256'], options={"verify_exp": False})
            jti = payload.get('jti')
            if jti:
                redis_client.set(f"blacklist_{jti}", "1", ex=86400)
        except Exception as _e:
            _log.warning({"event": "jwt_blacklist_failed", "details": str(_e)})
    return jsonify({"ok": True}), 200
