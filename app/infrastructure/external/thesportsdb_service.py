import os
import requests
import logging

logger = logging.getLogger(__name__)

class TheSportsDBService:
    def __init__(self):
        self.api_key = os.environ.get("THESPORTSDB_API_KEY", "3")
        self.base_url = f"https://www.thesportsdb.com/api/v1/json/{self.api_key}"

    def get_player_cutout(self, player_name: str) -> str:
        """
        Searches for a player by name and returns their cutout image URL (strCutout).
        Returns None if not found or on error.
        """
        if not player_name or player_name.lower() in ("badge", "team photo", "logo"):
            return None

        # Clean name for search (replace spaces with underscores or just use requests params)
        try:
            url = f"{self.base_url}/searchplayers.php"
            resp = requests.get(url, params={"p": player_name}, timeout=5)
            resp.raise_for_status()
            data = resp.json()
            
            players = data.get("player")
            if players and len(players) > 0:
                # Prioritize the one with the cutout
                for p in players:
                    cutout = p.get("strCutout")
                    if cutout:
                        return cutout
                # Fallback to thumb if no cutout
                return players[0].get("strThumb")
                
        except Exception as e:
            logger.error(f"Error fetching player from TheSportsDB: {e}")
        
        return None
