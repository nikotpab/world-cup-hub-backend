import redis
import os

# Idealmente conectado a una variable de entorno, ej REDIS_URL=redis://localhost:6379/0
redis_url = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')

class RedisCache:
    def __init__(self):
        try:
            self.client = redis.from_url(redis_url, decode_responses=True)
        except Exception:
            # Fallback en caso de que redis no esté disponible para no romper el piloto local
            self.client = None

    def get(self, key):
        if not self.client:
            return None
        try:
            return self.client.get(key)
        except Exception:
            return None

    def set(self, key, value, ex=None):
        if not self.client:
            return
        try:
            self.client.set(key, value, ex=ex)
        except Exception:
            pass

redis_client = RedisCache()
