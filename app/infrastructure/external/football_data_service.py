import os
import json
import time
import requests
from app.infrastructure.logger import app_logger

WC_CODE = "WC"
_CACHE_TTL = 300  # 5 minutes
_NOTE_PROVISIONAL = "Datos provisionales"


class FootballDataService:
    def __init__(self):
        self.api_url = os.environ.get("FOOTBALL_API_URL", "https://api.football-data.org/v4").rstrip("/")
        self.api_key = os.environ.get("FOOTBALL_API_KEY", "")

    def _headers(self):
        h = {"Accept": "application/json"}
        if self.api_key:
            h["X-Auth-Token"] = self.api_key
        return h

    # ------------------------------------------------------------------
    # Redis cache helpers
    # ------------------------------------------------------------------

    def _cache_get(self, key: str):
        try:
            from app.infrastructure.cache.redis_client import redis_client
            raw = redis_client.get(key)
            if raw:
                return json.loads(raw)
        except Exception as _e:
            app_logger.debug({"event": "football_cache_get_failed", "details": str(_e)})
        return None

    def _cache_set(self, key: str, value, ttl: int = _CACHE_TTL):
        try:
            from app.infrastructure.cache.redis_client import redis_client
            redis_client.set(key, json.dumps(value), ex=ttl)
        except Exception as _e:
            app_logger.debug({"event": "football_cache_set_failed", "details": str(_e)})

    def _cache_key(self, path: str, params: dict = None) -> str:
        suffix = "&".join(f"{k}={v}" for k, v in sorted((params or {}).items()))
        return f"football:{path}:{suffix}"

    # ------------------------------------------------------------------
    # HTTP
    # ------------------------------------------------------------------

    def _get(self, path: str, params: dict = None):
        if not self.api_key:
            return None
        cache_key = self._cache_key(path, params)
        cached = self._cache_get(cache_key)
        if cached:
            return cached

        url = f"{self.api_url}{path}"
        try:
            resp = requests.get(url, headers=self._headers(), params=params, timeout=12)
            resp.raise_for_status()
            data = resp.json()
            self._cache_set(cache_key, data)
            return data
        except requests.HTTPError as e:
            app_logger.error({"event": "football_api_http_error", "url": url, "status": e.response.status_code})
            return self._stale_or_none(cache_key)
        except requests.RequestException as e:
            app_logger.error({"event": "football_api_error", "url": url, "details": str(e)})
            return self._stale_or_none(cache_key)

    def _stale_or_none(self, cache_key: str):
        """Return stale cache with a warning note if available, else None."""
        try:
            from app.infrastructure.cache.redis_client import redis_client
            raw = redis_client.get(f"stale:{cache_key}")
            if raw:
                data = json.loads(raw)
                data["note"] = f"{_NOTE_PROVISIONAL} — última actualización pendiente"
                return data
        except Exception as _e:
            app_logger.debug({"event": "football_stale_cache_failed", "details": str(_e)})
        return None

    def _get_with_stale(self, path: str, params: dict = None):
        """Fetch, store a stale copy, and return data with graceful degradation."""
        cache_key = self._cache_key(path, params)
        data = self._cache_get(cache_key)
        if data:
            return data

        if not self.api_key:
            return None

        url = f"{self.api_url}{path}"
        try:
            resp = requests.get(url, headers=self._headers(), params=params, timeout=12)
            resp.raise_for_status()
            data = resp.json()
            self._cache_set(cache_key, data, ttl=_CACHE_TTL)
            # also keep as stale copy for much longer (1 hour)
            try:
                from app.infrastructure.cache.redis_client import redis_client
                redis_client.set(f"stale:{cache_key}", json.dumps(data), ex=3600)
            except Exception as _e:
                app_logger.debug({"event": "football_stale_write_failed", "details": str(_e)})
            return data
        except Exception as e:
            app_logger.warning({"event": "football_api_degraded", "details": str(e)})
            return self._stale_or_none(cache_key)

    # ------------------------------------------------------------------
    # Matches
    # ------------------------------------------------------------------

    def get_upcoming_matches(self):
        data = self._get_with_stale(f"/competitions/{WC_CODE}/matches", params={"status": "SCHEDULED"})
        if data:
            app_logger.info({"event": "football_api_matches_fetched", "count": len(data.get("matches", []))})
            return data
        return self._mock_matches()

    def get_live_matches(self):
        data = self._get_with_stale(f"/competitions/{WC_CODE}/matches", params={"status": "IN_PLAY,LIVE"})
        if data:
            return data
        return {"matches": [], "note": f"Sin partidos en vivo ({_NOTE_PROVISIONAL.lower()})"}

    def get_match(self, match_id: int):
        return self._get_with_stale(f"/matches/{match_id}")

    # ------------------------------------------------------------------
    # Teams & squads
    # ------------------------------------------------------------------

    def get_teams(self):
        data = self._get_with_stale(f"/competitions/{WC_CODE}/teams")
        if data:
            return data
        return {"teams": [
            {"id": 762, "name": "Argentina",  "shortName": "Argentina",  "tla": "ARG"},
            {"id": 759, "name": "Brazil",     "shortName": "Brazil",     "tla": "BRA"},
            {"id": 760, "name": "Colombia",   "shortName": "Colombia",   "tla": "COL"},
            {"id": 765, "name": "Spain",      "shortName": "Spain",      "tla": "ESP"},
            {"id": 773, "name": "Germany",    "shortName": "Germany",    "tla": "GER"},
            {"id": 770, "name": "France",     "shortName": "France",     "tla": "FRA"},
            {"id": 764, "name": "England",    "shortName": "England",    "tla": "ENG"},
            {"id": 799, "name": "USA",        "shortName": "USA",        "tla": "USA"},
            {"id": 801, "name": "Mexico",     "shortName": "Mexico",     "tla": "MEX"},
            {"id": 771, "name": "Portugal",   "shortName": "Portugal",   "tla": "POR"},
        ], "note": _NOTE_PROVISIONAL}

    def get_team_with_squad(self, team_id: int):
        data = self._get_with_stale(f"/teams/{team_id}")
        if data:
            return data
        return {"squad": []}

    # ------------------------------------------------------------------
    # Standings
    # ------------------------------------------------------------------

    def get_standings(self):
        return self._get_with_stale(f"/competitions/{WC_CODE}/standings")

    # ------------------------------------------------------------------
    # Mock fallback
    # ------------------------------------------------------------------

    @staticmethod
    def _mock_matches():
        return {
            "matches": [
                {
                    "id": 1, "status": "SCHEDULED",
                    "utcDate": "2026-06-11T20:00:00Z",
                    "homeTeam": {"name": "Mexico",  "tla": "MEX"},
                    "awayTeam": {"name": "Canada",  "tla": "CAN"},
                    "score": {"fullTime": {"home": None, "away": None}},
                    "note": _NOTE_PROVISIONAL,
                },
                {
                    "id": 2, "status": "SCHEDULED",
                    "utcDate": "2026-06-12T20:00:00Z",
                    "homeTeam": {"name": "Argentina", "tla": "ARG"},
                    "awayTeam": {"name": "Colombia",  "tla": "COL"},
                    "score": {"fullTime": {"home": None, "away": None}},
                    "note": _NOTE_PROVISIONAL,
                },
            ],
            "note": f"{_NOTE_PROVISIONAL} — API no configurada",
        }
