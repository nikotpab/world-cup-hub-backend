import pytest
from unittest.mock import MagicMock
from app.application.services.community_service import CommunityService
from app.application.dtos.community_dto import CommunityCreateDTO
from app.domain.models.community import Community
from app.domain.models.user import User

@pytest.fixture
def mock_repo():
    return MagicMock()

@pytest.fixture
def community_service(mock_repo):
    return CommunityService(mock_repo)

def test_create_community_success(community_service, mock_repo):
    # Setup
    user = User(userId=5, firstName="John", lastName="Doe")
    mock_repo.get_user_by_id.return_value = user
    
    def save_community_side_effect(community):
        community.community_id = 100
        return community
    mock_repo.save_community.side_effect = save_community_side_effect
    
    data = {"name": "Friends Pool", "userId": 5}
    
    # Execute
    result = community_service.create_community(data)
    
    # Assert
    assert result.name == "Friends Pool"
    assert result.community_id == 100
    assert 10000 <= result.invitation_code <= 99999
    mock_repo.save_community.assert_called_once()

def test_calculate_ranking_logic(community_service, mock_repo):
    # Setup ranking data
    mock_repo.get_community_ranking.return_value = [
        {"userId": 1, "name": "User 1", "points": 10},
        {"userId": 2, "name": "User 2", "points": 5}
    ]
    
    # Execute
    result = community_service.get_ranking(10)
    
    # Assert
    assert len(result) == 2
    assert result[0].points == 10
    assert result[1].userId == 2
