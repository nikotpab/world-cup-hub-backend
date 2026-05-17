import pytest
from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock
from app.application.services.bet_service import BetService
from app.application.dtos.bet_dto import BetCreateDTO
from app.domain.models.match import Match
from app.domain.models.bet import Bet
from app.domain.models.user import User

@pytest.fixture
def mock_repo():
    return MagicMock()

@pytest.fixture
def bet_service(mock_repo):
    return BetService(mock_repo)

def test_create_bet_success(bet_service, mock_repo):
    # Setup
    match_time = datetime.now(timezone.utc).replace(tzinfo=None) + timedelta(hours=1)
    match = Match(matchId=1, scheduledAt=match_time)
    mock_repo.get_match_by_id.return_value = match
    mock_repo.get_bet_by_user_match.return_value = None
    
    def save_bet_side_effect(bet):
        bet.bet_id = 1
        bet.version_id = 1
        return bet
    mock_repo.save_bet.side_effect = save_bet_side_effect
    
    data = {
        "homeGoals": 2,
        "awayGoals": 1,
        "matchId": 1,
        "userId": 5
    }
    
    # Execute
    result = bet_service.create_bet(data)
    
    # Assert
    assert result.home_goals == 2
    assert result.bet_id == 1
    mock_repo.save_bet.assert_called_once()
    mock_repo.commit.assert_called_once()

def test_create_bet_too_late(bet_service, mock_repo):
    # Setup: Match starts in 10 minutes (closure is 15 min before)
    match_time = datetime.now(timezone.utc).replace(tzinfo=None) + timedelta(minutes=10)
    match = Match(matchId=1, scheduledAt=match_time)
    mock_repo.get_match_by_id.return_value = match
    
    data = {"homeGoals": 1, "awayGoals": 0, "matchId": 1, "userId": 1}
    
    # Execute & Assert
    with pytest.raises(ValueError) as exc:
        bet_service.create_bet(data)
    assert "ha expirado" in str(exc.value)
