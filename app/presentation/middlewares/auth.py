from functools import wraps
from flask import request, jsonify, current_app
from app.infrastructure.cache.redis_client import redis_client
import jwt

def require_role(allowed_roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            token = request.headers.get('Authorization')
            if not token or not token.startswith('Bearer '):
                return jsonify({"error": "Token missing or invalid format"}), 401
                
            token = token.replace('Bearer ', '')
            
            try:
                secret_key = current_app.config.get('JWT_SECRET_KEY') or current_app.config.get('SECRET_KEY')
                payload = jwt.decode(token, secret_key, algorithms=['HS256'])
                
                # 1. Validar Blacklist en Redis (Si el Redis está caído, podría saltarse o rechazar por defecto)
                if redis_client.get(f"blacklist_{payload.get('jti')}"):
                    return jsonify({"error": "Token revoked"}), 401
                    
                # 2. Validar RBAC
                user_role_id = payload.get('roleId')
                # Simplificación para el piloto, asumiendo mapeo Role ID -> Nombre en el contexto real.
                # Aquí verificamos si user_role_id pertenece a allowed_roles (ej: 1 == Admin)
                if user_role_id not in allowed_roles:
                    return jsonify({"error": "Forbidden: Requires privilege"}), 403
                    
            except jwt.ExpiredSignatureError:
                return jsonify({"error": "Token expired"}), 401
            except jwt.InvalidTokenError:
                return jsonify({"error": "Invalid token"}), 401
                
            return f(*args, **kwargs) # Idealmente inyectamos current_user
        return decorated_function
    return decorator
