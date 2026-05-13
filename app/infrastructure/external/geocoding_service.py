import requests
from app.infrastructure.logger import app_logger

class NominatimGeocodingService:
    def __init__(self):
        # OpenStreetMap / Nominatim API base URL
        self.base_url = "https://nominatim.openstreetmap.org/search"
        # Requiere User-Agent para cumplir políticas de uso
        self.headers = {
            'User-Agent': 'Mundial2026Hub/1.0 (academic project)'
        }

    def search_city_or_stadium(self, query: str):
        try:
            params = {
                'q': query,
                'format': 'json',
                'limit': 5
            }
            response = requests.get(self.base_url, params=params, headers=self.headers, timeout=5)
            response.raise_for_status()
            results = response.json()
            
            app_logger.info({"event": "geocoding_search", "query": query, "results_count": len(results)})
            return results
        except requests.RequestException as e:
            app_logger.error({"event": "geocoding_error", "details": str(e)})
            return []
