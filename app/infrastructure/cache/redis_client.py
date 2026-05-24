"""
Cache con dos niveles:
  1. Redis (preferido) — compartido entre procesos / workers.
  2. In-process dict  — fallback automático cuando Redis no está disponible.
     Respeta TTL via time.monotonic() para no servir datos infinitamente.
"""
import logging
import os
import time
import threading

import redis

_log = logging.getLogger(__name__)

_mem: dict = {}          # {key: (value_str, expires_monotonic_or_None)}
_mem_lock = threading.Lock()


def _mem_get(key: str):
    with _mem_lock:
        entry = _mem.get(key)
        if entry is None:
            return None
        val, exp = entry
        if exp is not None and time.monotonic() > exp:
            _mem.pop(key, None)
            return None
        return val


def _mem_set(key: str, value: str, ex: int = None):
    with _mem_lock:
        exp = time.monotonic() + ex if ex else None
        _mem[key] = (value, exp)


class RedisCache:
    def __init__(self):
        redis_url = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
        try:
            self.client = redis.from_url(
                redis_url,
                decode_responses=True,
                socket_connect_timeout=2,
                socket_timeout=2,
            )
            self.client.ping()          # falla rápido si Redis no responde
        except Exception as _e:
            _log.debug("Redis unavailable, falling back to in-memory cache: %s", _e)
            self.client = None          # caeremos al fallback en memoria

    def get(self, key: str):
        if self.client:
            try:
                result = self.client.get(key)
                if result is not None:
                    return result
            except Exception as _e:
                _log.debug("Redis get failed, using in-memory fallback: %s", _e)
        return _mem_get(key)

    def set(self, key: str, value: str, ex: int = None):
        if self.client:
            try:
                self.client.set(key, value, ex=ex)
                return
            except Exception as _e:
                _log.debug("Redis set failed, using in-memory fallback: %s", _e)
        _mem_set(key, value, ex)

    def delete(self, key: str):
        if self.client:
            try:
                self.client.delete(key)
            except Exception as _e:
                _log.debug("Redis delete failed: %s", _e)
        with _mem_lock:
            _mem.pop(key, None)

    @property
    def available(self) -> bool:
        return self.client is not None


redis_client = RedisCache()
