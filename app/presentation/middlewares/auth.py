from functools import wraps
from flask import request, jsonify, current_app, g
from app.infrastructure.cache.redis_client import redis_client
import jwt


def _decode_token():
    """Decodes the Bearer token from the request. Returns payload or raises jwt exceptions."""
    auth_header = request.headers.get('Authorization', '')
    if not auth_header.startswith('Bearer '):
        raise ValueError("Token missing or invalid format")
    token = auth_header[7:]
    secret_key = current_app.config.get('JWT_SECRET_KEY') or current_app.config.get('SECRET_KEY')
    payload = jwt.decode(token, secret_key, algorithms=['HS256'])
    jti = payload.get('jti')
    if jti and redis_client.get(f"blacklist_{jti}"):
        raise PermissionError("Token revoked")
    return payload


def require_auth(f):
    """Validates JWT and injects g.user_id and g.role_id into the request context."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            payload = _decode_token()
        except ValueError as e:
            return jsonify({"error": str(e)}), 401
        except PermissionError as e:
            return jsonify({"error": str(e)}), 401
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid token"}), 401
        g.user_id = payload.get('userId')
        g.role_id = payload.get('roleId')
        return f(*args, **kwargs)
    return decorated_function


def require_role(allowed_roles):
    """Validates JWT and enforces role membership."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                payload = _decode_token()
            except ValueError as e:
                return jsonify({"error": str(e)}), 401
            except PermissionError as e:
                return jsonify({"error": str(e)}), 401
            except jwt.ExpiredSignatureError:
                return jsonify({"error": "Token expired"}), 401
            except jwt.InvalidTokenError:
                return jsonify({"error": "Invalid token"}), 401
            if payload.get('roleId') not in allowed_roles:
                return jsonify({"error": "Forbidden: Requires privilege"}), 403
            g.user_id = payload.get('userId')
            g.role_id = payload.get('roleId')
            return f(*args, **kwargs)
        return decorated_function
    return decorator
