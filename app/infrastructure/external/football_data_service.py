import os
import requests
from app.infrastructure.logger import app_logger

WC_CODE = "WC"


class FootballDataService:
    def __init__(self):
        self.api_url = os.environ.get("FOOTBALL_API_URL", "https://api.football-data.org/v4").rstrip("/")
        self.api_key = os.environ.get("FOOTBALL_API_KEY", "")

    def _headers(self):
        h = {"Accept": "application/json"}
        if self.api_key:
            h["X-Auth-Token"] = self.api_key
        return h

    def _get(self, path: str, params: dict = None):
        if not self.api_key:
            return None  # caller decides fallback
        url = f"{self.api_url}{path}"
        try:
            resp = requests.get(url, headers=self._headers(), params=params, timeout=12)
            resp.raise_for_status()
            return resp.json()
        except requests.HTTPError as e:
            app_logger.error({"event": "football_api_http_error", "url": url, "status": e.response.status_code})
            return None
        except requests.RequestException as e:
            app_logger.error({"event": "football_api_error", "url": url, "details": str(e)})
            return None

    # ------------------------------------------------------------------
    # Matches
    # ------------------------------------------------------------------

    def get_upcoming_matches(self):
        data = self._get(f"/competitions/{WC_CODE}/matches", params={"status": "SCHEDULED"})
        if data:
            app_logger.info({"event": "football_api_matches_fetched", "count": len(data.get("matches", []))})
            return data
        return self._mock_matches()

    def get_live_matches(self):
        data = self._get(f"/competitions/{WC_CODE}/matches", params={"status": "IN_PLAY,LIVE"})
        if data:
            return data
        return {"matches": [], "note": "Sin partidos en vivo (datos provisionales)"}

    def get_match(self, match_id: int):
        data = self._get(f"/matches/{match_id}")
        return data  # puede ser None si la API falla

    # ------------------------------------------------------------------
    # Teams & squads
    # ------------------------------------------------------------------

    def get_teams(self):
        data = self._get(f"/competitions/{WC_CODE}/teams")
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
        ], "note": "Datos provisionales"}

    def get_team_with_squad(self, team_id: int):
        data = self._get(f"/teams/{team_id}")
        if data:
            return data
        return {"squad": []}

    # ------------------------------------------------------------------
    # Standings
    # ------------------------------------------------------------------

    def get_standings(self):
        data = self._get(f"/competitions/{WC_CODE}/standings")
        return data  # None si falla

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
                    "note": "Datos provisionales",
                },
                {
                    "id": 2, "status": "SCHEDULED",
                    "utcDate": "2026-06-12T20:00:00Z",
                    "homeTeam": {"name": "Argentina", "tla": "ARG"},
                    "awayTeam": {"name": "Colombia",  "tla": "COL"},
                    "score": {"fullTime": {"home": None, "away": None}},
                    "note": "Datos provisionales",
                },
            ],
            "note": "Datos provisionales — API no configurada",
        }
