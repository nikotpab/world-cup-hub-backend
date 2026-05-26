"""
OpenStreetMap / Nominatim geocoding service.
Converts city/stadium names to lat/lon coordinates.
Results cached 30 days in Redis — stadiums rarely move.
Respects Nominatim ToS: 1 req/s max, User-Agent required.
"""
import time
import json
import requests
from app.infrastructure.logger import app_logger

_NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
_CACHE_TTL = 86400 * 30  # 30 days
_LAST_REQUEST_TIME = 0.0
_MIN_INTERVAL = 1.1  # seconds between requests (rate limit)

_HEADERS = {
    "User-Agent": "WorldCupHub/1.0 (contact: worldcuphub2026@gmail.com)",
    "Accept-Language": "es,en",
}


def _cache_key(query: str) -> str:
    return f"geo:nominatim:{query.lower().strip()}"


def _throttle() -> None:
    global _LAST_REQUEST_TIME
    elapsed = time.time() - _LAST_REQUEST_TIME
    if elapsed < _MIN_INTERVAL:
        time.sleep(_MIN_INTERVAL - elapsed)
    _LAST_REQUEST_TIME = time.time()


def geocode(query: str) -> dict | None:
    """
    Returns {"lat": float, "lon": float, "display_name": str} or None.
    Query can be a city name, stadium name, or free-form address.
    """
    from app.infrastructure.cache.redis_client import redis_client

    cache_key = _cache_key(query)
    try:
        cached = redis_client.get(cache_key)
        if cached:
            return json.loads(cached)
    except Exception:
        pass

    _throttle()
    try:
        resp = requests.get(
            _NOMINATIM_URL,
            params={"q": query, "format": "json", "limit": 1},
            headers=_HEADERS,
            timeout=8,
        )
        resp.raise_for_status()
        results = resp.json()
        if not results:
            return None

        first = results[0]
        data = {
            "lat": float(first["lat"]),
            "lon": float(first["lon"]),
            "display_name": first.get("display_name", query),
        }
        try:
            redis_client.set(cache_key, json.dumps(data), ex=_CACHE_TTL)
        except Exception:
            pass
        return data

    except Exception as exc:
        app_logger.warning({"event": "geocoding_failed", "query": query, "details": str(exc)})
        return None


def geocode_stadium(stadium_name: str, city_name: str | None = None) -> dict | None:
    query = f"{stadium_name}, {city_name}" if city_name else stadium_name
    return geocode(query)


def geocode_city(city_name: str) -> dict | None:
    return geocode(city_name)
