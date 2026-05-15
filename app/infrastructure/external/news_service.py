"""
Proxy hacia NewsAPI para noticias del Mundial 2026.
La key nunca sale del backend — Flutter sólo habla con /api/v1/news.
Resultados cacheados 15 min en Redis para no quemar el plan gratuito.
"""
import os
import json
import requests
from app.infrastructure.logger import app_logger

_CACHE_KEY = "news:wc2026"
_CACHE_TTL  = 900   # 15 minutos
_PAGE_SIZE  = 15

# Términos que garantizan relevancia exclusiva al Mundial 2026
_QUERY = (
    '"Mundial 2026" OR "World Cup 2026" OR "FIFA 2026" OR '
    '"Copa del Mundo 2026" OR "FIFA World Cup 2026"'
)


class NewsService:
    def __init__(self):
        self.api_key = os.environ.get("NEWS_API_KEY", "")
        self.base_url = "https://newsapi.org/v2/everything"

    def get_wc2026_news(self) -> list:
        """Devuelve lista de artículos. Usa caché Redis cuando está disponible."""
        cached = self._cache_get()
        if cached is not None:
            return cached

        if not self.api_key:
            app_logger.warning({"event": "news_api_key_missing"})
            return self._mock_articles()

        try:
            resp = requests.get(
                self.base_url,
                params={
                    "q": _QUERY,
                    "language": "es",
                    "sortBy": "publishedAt",
                    "pageSize": _PAGE_SIZE,
                    "apiKey": self.api_key,
                },
                timeout=10,
            )
            resp.raise_for_status()
            data = resp.json()
            articles = self._normalize(data.get("articles", []))
            self._cache_set(articles)
            return articles
        except requests.HTTPError as e:
            app_logger.error({"event": "news_api_http_error", "status": e.response.status_code})
        except Exception as e:
            app_logger.error({"event": "news_api_error", "details": str(e)})

        # Si falla, intenta servir caché vencida antes de ir al mock
        stale = self._cache_get(stale=True)
        if stale:
            return stale
        return self._mock_articles()

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _normalize(raw: list) -> list:
        out = []
        for a in raw:
            if not a.get("title") or a.get("title") == "[Removed]":
                continue
            out.append({
                "title":       a.get("title", ""),
                "description": a.get("description") or "",
                "url":         a.get("url", ""),
                "imageUrl":    a.get("urlToImage") or "",
                "source":      a.get("source", {}).get("name", ""),
                "publishedAt": a.get("publishedAt", ""),
            })
        return out

    def _cache_get(self, stale: bool = False):
        try:
            from app.infrastructure.cache.redis_client import redis_client
            key = f"stale:{_CACHE_KEY}" if stale else _CACHE_KEY
            raw = redis_client.get(key)
            if raw:
                return json.loads(raw)
        except Exception:
            pass
        return None

    def _cache_set(self, articles: list) -> None:
        try:
            from app.infrastructure.cache.redis_client import redis_client
            payload = json.dumps(articles)
            redis_client.set(_CACHE_KEY, payload, ex=_CACHE_TTL)
            redis_client.set(f"stale:{_CACHE_KEY}", payload, ex=86400)  # 24h stale
        except Exception:
            pass

    @staticmethod
    def _mock_articles() -> list:
        return [
            {
                "title": "FIFA confirma los 48 equipos clasificados al Mundial 2026",
                "description": "La FIFA publicó la lista oficial de selecciones que participarán en la Copa del Mundo 2026, que se celebrará en Estados Unidos, México y Canadá.",
                "url": "",
                "imageUrl": "",
                "source": "FIFA",
                "publishedAt": "2026-01-01T00:00:00Z",
            },
            {
                "title": "Los estadios del Mundial 2026: capacidades y sedes confirmadas",
                "description": "Dieciséis estadios repartidos entre tres países acogerán los partidos del torneo más grande de la historia del fútbol.",
                "url": "",
                "imageUrl": "",
                "source": "Mundial Hub",
                "publishedAt": "2026-01-02T00:00:00Z",
            },
            {
                "title": "El formato inédito: 104 partidos y 48 selecciones",
                "description": "Por primera vez en la historia, el Mundial amplía su formato a 48 equipos distribuidos en 12 grupos de cuatro selecciones.",
                "url": "",
                "imageUrl": "",
                "source": "Mundial Hub",
                "publishedAt": "2026-01-03T00:00:00Z",
            },
        ]


news_service = NewsService()
