import pytest
from unittest.mock import MagicMock, patch
from werkzeug.security import generate_password_hash
from src.AuthenticationService import AuthenticationService

class TestAuthenticationService:

    @patch('src.AuthenticationService.get_db')
    def test_register_success(self, mock_get_db):
        mock_conn = MagicMock()
        mock_cur = mock_conn.cursor.return_value
        mock_get_db.return_value = mock_conn
        mock_cur.fetchone.return_value = None
        (success, message) = AuthenticationService.register('nuevo_pro', 'password123', 'test@mundial.com')
        assert success is True
        assert message == 'Success'
        mock_conn.commit.assert_called_once()

    @patch('src.AuthenticationService.get_db')
    def test_register_invalid_email(self, mock_get_db):
        (success, message) = AuthenticationService.register('user', 'pass', 'esto-no-es-un-email')
        assert success is False
        assert 'Invalid email' in message

    @patch('src.AuthenticationService.get_db')
    def test_register_user_exists(self, mock_get_db):
        mock_conn = MagicMock()
        mock_cur = mock_conn.cursor.return_value
        mock_get_db.return_value = mock_conn
        mock_cur.fetchone.return_value = {'username': 'messi'}
        (success, message) = AuthenticationService.register('messi', '123', 'leo@test.com')
        assert success is False
        assert 'already exists' in message

    @patch('src.AuthenticationService.get_db')
    def test_login_success(self, mock_get_db):
        mock_conn = MagicMock()
        mock_cur = mock_conn.cursor.return_value
        mock_get_db.return_value = mock_conn
        pw_plana = 'goat10'
        hash_db = generate_password_hash(pw_plana)
        mock_cur.fetchone.return_value = {'username': 'leo', 'password': hash_db}
        account = AuthenticationService.login('leo', pw_plana)
        assert account is not None
        assert account['username'] == 'leo'

    @patch('src.AuthenticationService.get_db')
    def test_login_wrong_password(self, mock_get_db):
        mock_conn = MagicMock()
        mock_cur = mock_conn.cursor.return_value
        mock_get_db.return_value = mock_conn
        hash_real = generate_password_hash('password_correcto')
        mock_cur.fetchone.return_value = {'username': 'admin', 'password': hash_real}
        account = AuthenticationService.login('admin', 'soy-un-hacker')
        assert account is None

    @patch('src.AuthenticationService.get_db')
    def test_login_user_not_found(self, mock_get_db):
        mock_conn = MagicMock()
        mock_cur = mock_conn.cursor.return_value
        mock_get_db.return_value = mock_conn
        mock_cur.fetchone.return_value = None
        account = AuthenticationService.login('fantasma', '1234')
        assert account is None
