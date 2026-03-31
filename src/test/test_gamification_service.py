import pytest
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock
from src.services.GamificationService import GamificationService, GamificationError

@pytest.fixture
def mock_match():
    match = MagicMock()
    match.matchId = 1
    match.scheduledAt = datetime.utcnow() + timedelta(hours=2)
    return match

@pytest.fixture
def mock_pack():
    pack = MagicMock()
    pack.packId = 1
    pack.userId = 42
    pack.stickers = []
    return pack

class TestGamificationService:

    @patch('src.database.db.session.add')
    @patch('src.database.db.session.commit')
    @patch('src.models.prediction.Prediction.query')
    @patch('src.models.match.Match.query')
    def test_submit_prediction_success(self, mock_match_query, mock_pred_query, mock_commit, mock_add, mock_match):
        mock_match_query.get.return_value = mock_match
        mock_pred_query.filter_by.return_value.first.return_value = None

        prediction = GamificationService.submit_prediction(1, 42, 2, 1, 99)

        assert mock_add.call_count == 1
        assert mock_commit.call_count == 1
        assert prediction.homeGoals == 2
        assert prediction.awayGoals == 1

    @patch('src.models.match.Match.query')
    def test_submit_prediction_late(self, mock_match_query, mock_match):
        mock_match.scheduledAt = datetime.utcnow() - timedelta(minutes=10)
        mock_match_query.get.return_value = mock_match

        with pytest.raises(GamificationError) as excinfo:
            GamificationService.submit_prediction(1, 42, 2, 1, 99)

        assert excinfo.value.status_code == 403
        assert "ya ha comenzado" in str(excinfo.value)

    @patch('src.database.db.session.add')
    @patch('src.database.db.session.commit')
    @patch('src.models.sticker.Sticker.query')
    @patch('src.models.album.Album.query')
    @patch('src.models.pack.Pack.query')
    def test_open_pack_success(self, mock_pack_query, mock_album_query, mock_sticker_query, mock_commit, mock_add, mock_pack):
        mock_pack_query.filter_by.return_value.first.return_value = mock_pack
        
        album = MagicMock()
        album.stickers = []
        mock_album_query.filter_by.return_value.first.return_value = album
        
        mock_stickers = [MagicMock(stickerId=i) for i in range(1, 10)]
        mock_sticker_query.all.return_value = mock_stickers

        result = GamificationService.open_pack(1, 42)

        assert result["success"] is True
        assert len(result["stickers"]) == 5
        assert len(mock_pack.stickers) == 5
        assert mock_commit.call_count >= 1

    @patch('src.models.pack.Pack.query')
    def test_open_pack_already_opened(self, mock_pack_query, mock_pack):
        mock_pack.stickers = [MagicMock()]
        mock_pack_query.filter_by.return_value.first.return_value = mock_pack

        with pytest.raises(GamificationError) as excinfo:
            GamificationService.open_pack(1, 42)

        assert excinfo.value.status_code == 400
        assert "ya ha sido abierto" in str(excinfo.value)
