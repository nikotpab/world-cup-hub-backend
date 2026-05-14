import os
import requests
from app.infrastructure.logger import app_logger

class FootballDataService:
    def __init__(self):
        # Utilizando football-data.org o thesportsdb como ejemplo
        self.api_url = os.environ.get('FOOTBALL_API_URL', 'https://api.football-data.org/v4')
        self.api_key = os.environ.get('FOOTBALL_API_KEY')
        
    def get_headers(self):
        headers = {}
        if self.api_key:
            headers['X-Auth-Token'] = self.api_key # header típico de football-data
        return headers

    def get_upcoming_matches(self, competition_id: str = '2000'): # 2000 es el id de la WC típicamente
        try:
            if not self.api_key:
                app_logger.info({"event": "football_data_simulated", "action": "get_upcoming_matches"})
                return self._get_mock_matches()
                
            response = requests.get(f"{self.api_url}/competitions/{competition_id}/matches", headers=self.get_headers(), timeout=10)
            response.raise_for_status()
            
            return response.json()
        except requests.RequestException as e:
            app_logger.error({"event": "football_api_error", "details": str(e)})
            return self._get_mock_matches()

    def get_teams(self, competition_id: str = '2000'):
        try:
            if not self.api_key:
                app_logger.info({"event": "football_data_simulated", "action": "get_teams"})
                return {"teams": [{"id": 1, "name": "Argentina", "tla": "ARG"}, {"id": 2, "name": "Brazil", "tla": "BRA"}]}
                
            response = requests.get(f"{self.api_url}/competitions/{competition_id}/teams", headers=self.get_headers(), timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            app_logger.error({"event": "football_api_error", "action": "get_teams", "details": str(e)})
            return {"teams": []}

    def get_team_players(self, team_id: int):
        try:
            if not self.api_key:
                app_logger.info({"event": "football_data_simulated", "action": "get_team_players", "team_id": team_id})
                return {"squad": [{"id": 101, "name": "Lionel Messi", "position": "Forward"}, {"id": 102, "name": "Angel Di Maria", "position": "Midfielder"}]}
                
            response = requests.get(f"{self.api_url}/teams/{team_id}", headers=self.get_headers(), timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            app_logger.error({"event": "football_api_error", "action": "get_team_players", "team_id": team_id, "details": str(e)})
            return {"squad": []}

    def _get_mock_matches(self):
        # Retorna datos confirmados estáticos (degradación con gracia)
        return {
            "matches": [
                {"id": 1, "homeTeam": {"name": "USA"}, "awayTeam": {"name": "Mexico"}, "status": "SCHEDULED"},
                {"id": 2, "homeTeam": {"name": "Canada"}, "awayTeam": {"name": "Panama"}, "status": "SCHEDULED"}
            ],
            "note": "Datos provisionales"
        }
