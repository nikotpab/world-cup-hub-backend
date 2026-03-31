import pytest
from datetime import datetime
from unittest.mock import patch, MagicMock
from src.services.MatchService import MatchService, MatchServiceError

@pytest.fixture
def mock_match():
    match = MagicMock()
    match.matchId = 1
    match.status = 'Previa'
    match.phase = 'Grupos'
    match.scheduledAt = datetime(2026, 6, 11, 20, 0, 0)
    return match

class TestMatchService:
    
    @patch('src.models.match.Match.query')
    def test_get_matches_by_phase(self, mock_query, mock_match):
        mock_query.filter_by.return_value.order_by.return_value.all.return_value = [mock_match]
        
        results = MatchService.get_matches_by_phase('Grupos')
        
        assert len(results) == 1
        assert results[0].phase == 'Grupos'
        mock_query.filter_by.assert_called_with(phase='Grupos')
        
    def test_convert_match_time_to_timezone(self):
        utc_time = datetime(2026, 6, 11, 20, 0, 0)
        local_est_time = MatchService.convert_match_time_to_timezone(utc_time, -5)
        assert local_est_time == "2026-06-11 15:00:00"

    @patch('src.database.db.session.commit')
    @patch('src.models.match.Match.query')
    def test_update_match_status_success(self, mock_query, mock_commit, mock_match):
        mock_query.get.return_value = mock_match
        
        updated_match = MatchService.update_match_status(1, 'En Curso')
        
        assert updated_match.status == 'En Curso'
        mock_commit.assert_called_once()
        mock_query.get.assert_called_with(1)

    @patch('src.models.match.Match.query')
    def test_update_match_status_not_found(self, mock_query):
        mock_query.get.return_value = None
        
        with pytest.raises(MatchServiceError) as excinfo:
            MatchService.update_match_status(999, 'En Curso')
        
        assert excinfo.value.status_code == 404
