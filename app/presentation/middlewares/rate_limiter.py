from functools import wraps
from flask import request, jsonify
from app.infrastructure.cache.redis_client import redis_client

def rate_limit(limit=10, window=60):
    """
    Limita la cantidad de peticiones permitidas por un cliente (IP) en una ventana de tiempo.
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not redis_client.client:
                # Si redis falla, permite pasar (Degradación con gracia)
                return f(*args, **kwargs)
                
            # Extraer la IP o User ID si estuviese autenticado
            client_ip = request.remote_addr
            endpoint_name = request.endpoint
            
            redis_key = f"rl_{endpoint_name}_{client_ip}"
            
            # Implementación Fixed Window sencilla
            current_requests = redis_client.client.get(redis_key)
            if current_requests and int(current_requests) >= limit:
                return jsonify({
                    "error": "ERR_TOO_MANY_REQUESTS", 
                    "message": "Has excedido el límite de solicitudes. Intenta más tarde."
                }), 429
                
            # Incrementar contador (atómico)
            pipeline = redis_client.client.pipeline()
            pipeline.incr(redis_key)
            if not current_requests:
                pipeline.expire(redis_key, window)
            pipeline.execute()
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator
