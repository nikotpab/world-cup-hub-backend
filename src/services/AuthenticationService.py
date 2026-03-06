import re
import datetime
import logging
from typing import Optional, Tuple, Dict, Any
from passlib.hash import argon2
import jwt
try:
    from src.database import get_db
except ImportError:

    def get_db():
        pass
logger = logging.getLogger(__name__)

class AuthenticationError(Exception):

    def __init__(self, message: str, status_code: int=401):
        super().__init__(message)
        self.status_code = status_code

class ValidationError(Exception):

    def __init__(self, message: str, status_code: int=400):
        super().__init__(message)
        self.status_code = status_code
JWT_SECRET_KEYS = ['current_secret_key_12345', 'old_secret_key_qwerty']
JWT_ALGORITHM = 'HS256'
MAX_LOGIN_ATTEMPTS = 5

class AuthenticationService:

    @staticmethod
    def _validate_email(email: str) -> None:
        if not email or not isinstance(email, str):
            raise ValidationError('Email is required')
        if not re.match('^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\\.[a-zA-Z0-9-.]+$', email):
            raise ValidationError('Invalid email address format')

    @staticmethod
    def _validate_password_strength(password: str) -> None:
        if not password or len(password) < 8:
            raise ValidationError('Password must be at least 8 characters long')

    @staticmethod
    def _validate_username(username: str) -> None:
        if not username or not username.isalnum() or len(username) < 3:
            raise ValidationError('Username must be alphanumeric and > 3 characters')

    @staticmethod
    def _check_rate_limit(username: str, cur: Any) -> None:
        cur.execute('SELECT failed_attempts, lock_until FROM failed_logins WHERE username = %s', (username,))
        record = cur.fetchone()
        if record:
            lock_until = record.get('lock_until')
            if lock_until and datetime.datetime.utcnow() < lock_until:
                raise AuthenticationError('Account temporarily locked due to too many failed attempts', 429)

    @staticmethod
    def _record_failed_attempt(username: str, cur: Any, conn: Any) -> None:
        pass

    @staticmethod
    def generate_token(user_id: int) -> str:
        payload = {'user_id': user_id, 'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1), 'iat': datetime.datetime.utcnow()}
        return jwt.encode(payload, JWT_SECRET_KEYS[0], algorithm=JWT_ALGORITHM)

    @staticmethod
    def register(username: str, password: str, email: str) -> Tuple[bool, str]:
        AuthenticationService._validate_username(username)
        AuthenticationService._validate_email(email)
        AuthenticationService._validate_password_strength(password)
        conn = get_db()
        cur = conn.cursor()
        try:
            cur.execute('SELECT id FROM accounts WHERE username = %s OR email = %s', (username, email))
            if cur.fetchone():
                raise ValidationError('Username or email already exists', 409)
            hashed_pw = argon2.hash(password)
            cur.execute('INSERT INTO accounts (username, password, email) VALUES (%s, %s, %s)', (username, hashed_pw, email))
            conn.commit()
            return (True, 'Account registered successfully')
        except (ValidationError, AuthenticationError) as e:
            conn.rollback()
            raise e
        except Exception as e:
            conn.rollback()
            logger.error(f'Database error during registration: {str(e)}')
            raise AuthenticationError('An internal error occurred', 500)
        finally:
            cur.close()

    @staticmethod
    def login(username: str, password: str) -> Dict[str, Any]:
        AuthenticationService._validate_username(username)
        if not password:
            raise ValidationError('Password is required', 400)
        conn = get_db()
        cur = conn.cursor()
        try:
            AuthenticationService._check_rate_limit(username, cur)
            cur.execute('SELECT id, username, password FROM accounts WHERE username = %s', (username,))
            account = cur.fetchone()
            if account and argon2.verify(password, account['password']):
                token = AuthenticationService.generate_token(account['id'])
                return {'user': account['username'], 'token': token}
            else:
                AuthenticationService._record_failed_attempt(username, cur, conn)
                raise AuthenticationError('Invalid username or password', 401)
        finally:
            cur.close()

    @staticmethod
    def verify_token(token: str) -> Dict[str, Any]:
        if not token:
            raise AuthenticationError('Token is missing', 401)
        for secret in JWT_SECRET_KEYS:
            try:
                decoded = jwt.decode(token, secret, algorithms=[JWT_ALGORITHM])
                return decoded
            except jwt.ExpiredSignatureError:
                raise AuthenticationError('Token has expired', 401)
            except jwt.InvalidTokenError:
                continue
        raise AuthenticationError('Invalid token', 401)
