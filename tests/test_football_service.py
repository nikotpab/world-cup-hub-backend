import pytest
import json
from unittest.mock import patch, MagicMock
import requests
from app.infrastructure.cache.redis_client import redis_client
from app.infrastructure.external.football_data_service import FootballDataService

@pytest.fixture(autouse=True)
def clean_cache():
    # Clean the in-memory cache fallback of redis_client before each test
    from app.infrastructure.cache.redis_client import _mem
    _mem.clear()
    yield

def test_football_service_success():
    service = FootballDataService()
    service.api_key = "test_key"
    
    mock_data = {"matches": [{"id": 123, "status": "SCHEDULED"}]}
    
    with patch("requests.get") as mock_get:
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = mock_data
        mock_get.return_value = mock_resp
        
        # Call the service
        res = service.get_upcoming_matches()
        
        # Verify request was made
        mock_get.assert_called_once()
        assert res == mock_data
        
        # Verify it was cached in primary cache
        cache_key = service._cache_key("/competitions/WC/matches", {"status": "SCHEDULED"})
        cached_primary = redis_client.get(cache_key)
        assert cached_primary is not None
        assert json.loads(cached_primary) == mock_data
        
        # Verify it was cached in stale cache
        cached_stale = redis_client.get(f"stale:{cache_key}")
        assert cached_stale is not None
        assert json.loads(cached_stale) == mock_data

def test_football_service_graceful_degradation():
    service = FootballDataService()
    service.api_key = "test_key"
    
    mock_data = {"matches": [{"id": 123, "status": "SCHEDULED"}]}
    cache_key = service._cache_key("/competitions/WC/matches", {"status": "SCHEDULED"})
    
    # Pre-populate stale cache
    redis_client.set(f"stale:{cache_key}", json.dumps(mock_data))
    
    with patch("requests.get") as mock_get:
        # Mock API raising an exception (e.g., rate limit or timeout)
        mock_get.side_effect = requests.RequestException("Rate Limit Exceeded")
        
        # Call the service
        res = service.get_upcoming_matches()
        
        # Verify it degraded gracefully returning stale cache + provisional note
        assert res is not None
        assert res["matches"] == mock_data["matches"]
        assert "note" in res
        assert "Datos provisionales" in res["note"]

def test_football_service_mock_fallback():
    service = FootballDataService()
    service.api_key = "test_key"
    
    # Ensure cache is empty (no primary, no stale)
    with patch("requests.get") as mock_get:
        mock_get.side_effect = requests.RequestException("API completely down")
        
        # Call the service
        res = service.get_upcoming_matches()
        
        # Verify it fell back to mock matches
        assert res is not None
        assert "matches" in res
        assert len(res["matches"]) > 0
        assert "Mexico" in res["matches"][0]["homeTeam"]["name"]
        assert "API no configurada" in res["note"]
