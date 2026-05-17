import pytest
from unittest.mock import patch, MagicMock
from argon2 import PasswordHasher

ph = PasswordHasher()
import jwt
import datetime
from datetime import timezone as _tz
from app.application.services.AuthenticationService import AuthenticationService, AuthenticationError, ValidationError, JWT_SECRET_KEYS

import sys

@pytest.fixture
def mock_db_cursor():
    _auth_svc_module = sys.modules['src.services.AuthenticationService']
    with patch.object(_auth_svc_module, 'get_db') as mock_get_db:
        mock_conn = MagicMock()
        mock_cur = MagicMock()
        mock_conn.cursor.return_value = mock_cur
        mock_get_db.return_value = mock_conn

        yield mock_cur, mock_conn

class TestAuthenticationService:
    
    def test_register_success(self, mock_db_cursor):
        mock_cur, mock_conn = mock_db_cursor
        mock_cur.fetchone.return_value = None
        
        success, message = AuthenticationService.register("newuser", "SecurePass123!", "test@example.com")
        
        assert success is True
        assert "successfully" in message
        mock_cur.execute.assert_called()
        mock_conn.commit.assert_called_once()

    def test_login_success(self, mock_db_cursor):
        mock_cur, mock_conn = mock_db_cursor
        setup_hashed_pw = ph.hash("SecurePass123!")
        
        mock_cur.fetchone.side_effect = [
            None,
            {'id': 1, 'username': 'testuser', 'password': setup_hashed_pw}
        ]
        
        result = AuthenticationService.login("testuser", "SecurePass123!")
        
        assert "token" in result
        assert result["user"] == "testuser"
    def test_register_invalid_email(self):
        with pytest.raises(ValidationError) as exc:
            AuthenticationService.register("newuser", "SecurePass123!", "invalid-email")
        assert exc.value.status_code == 400
        assert "Invalid email" in str(exc.value)

    def test_register_weak_password(self):
        with pytest.raises(ValidationError) as exc:
            AuthenticationService.register("newuser", "123", "test@example.com")
        assert exc.value.status_code == 400
        assert "characters" in str(exc.value)
        
    def test_login_invalid_credentials(self, mock_db_cursor):
        mock_cur, _ = mock_db_cursor
        setup_hashed_pw = ph.hash("SecurePass123!")
        
        mock_cur.fetchone.side_effect = [
            None,
            {'id': 1, 'username': 'testuser', 'password': setup_hashed_pw}
        ]
        
        with pytest.raises(AuthenticationError) as exc:
            AuthenticationService.login("testuser", "WrongPassword!")
        assert exc.value.status_code == 401
        assert "Invalid username or password" in str(exc.value)

    def test_login_rate_limit_blocked(self, mock_db_cursor):
        mock_cur, _ = mock_db_cursor
        mock_cur.fetchone.return_value = {
            'failed_attempts': 5, 
            'lock_until': datetime.datetime.now(_tz.utc).replace(tzinfo=None) + datetime.timedelta(minutes=15)
        }
        
        with pytest.raises(AuthenticationError) as exc:
            AuthenticationService.login("hackeduser", "AnyPassword123")
        assert exc.value.status_code == 429
        assert "temporarily locked" in str(exc.value)
        
    def test_verify_expired_token(self):
        payload = {
            'user_id': 1,
            'exp': datetime.datetime.now(_tz.utc) - datetime.timedelta(hours=1)
        }
        token = jwt.encode(payload, JWT_SECRET_KEYS[0], algorithm="HS256")
        
        with pytest.raises(AuthenticationError) as exc:
            AuthenticationService.verify_token(token)
        assert exc.value.status_code == 401
        assert "Token has expired" in str(exc.value)

    def test_verify_malformed_token(self):
        with pytest.raises(AuthenticationError) as exc:
            AuthenticationService.verify_token("not.a.real.jwt.token")
        assert exc.value.status_code == 401
        assert "Invalid token" in str(exc.value)
