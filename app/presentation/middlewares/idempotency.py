from functools import wraps
from flask import request, jsonify
from app.infrastructure.cache.redis_client import redis_client
import json

def idempotent_request(expire_seconds=86400):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if request.method not in ['POST', 'PUT', 'PATCH']:
                return f(*args, **kwargs)
                
            idempotency_key = request.headers.get('X-Idempotency-Key')
            if not idempotency_key:
                return f(*args, **kwargs)
                
            redis_key = f"idempotency_{idempotency_key}"
            
            # Lock atómico para prevenir condiciones de carrera al consultar la misma llave al mismo tiempo
            # (setnx = set if not exists)
            is_new = redis_client.client.setnx(redis_key + "_lock", "1") if redis_client.client else True
            if not is_new:
                return jsonify({"error": "ERR_CONCURRENT_REQUEST", "message": "Transaction currently processing"}), 409
                
            try:
                # Revisar si ya retornamos resultado
                if redis_client.client:
                    cached_response = redis_client.get(redis_key)
                    if cached_response:
                        cached_data = json.loads(cached_response)
                        return jsonify(cached_data["body"]), cached_data["status"]

                # Ejecutar la función original
                response, status_code = f(*args, **kwargs)
                
                # Cachear el resultado final
                if redis_client.client and status_code in (200, 201):
                    # Asume que response es de tipo jsonify o dict, en una API real requeriría extraer el JSON del obj Response
                    data_to_cache = {"body": response.get_json(), "status": status_code}
                    redis_client.set(redis_key, json.dumps(data_to_cache), ex=expire_seconds)
                
                return response, status_code
                
            finally:
                if redis_client.client:
                    redis_client.client.delete(redis_key + "_lock")
                    
        return decorated_function
    return decorator
