import re
from werkzeug.security import generate_password_hash, check_password_hash
from src.database import get_db

class AuthenticationService:
    @staticmethod
    def login(username, password):
        conn = get_db()
        cur = conn.cursor()
        
        cur.execute('SELECT * FROM accounts WHERE username = %s', (username,))
        account = cur.fetchone()
        cur.close()

        if account and check_password_hash(account['password'], password):
            return account
        return None

    @staticmethod
    def register(username, password, email):
        
        if not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            return False, 'Invalid email address!'
        
        conn = get_db()
        cur = conn.cursor()   
        
        cur.execute('SELECT * FROM accounts WHERE username = %s', (username,))
        if cur.fetchone():
            cur.close()
            return False, 'Account already exists!'
        
        hashed_pw = generate_password_hash(password)
        try:
            cur.execute(
                'INSERT INTO accounts (username, password, email) VALUES (%s, %s, %s)',
                (username, hashed_pw, email)
            )
            conn.commit()
            cur.close()
            return True, 'Success'
        except Exception as e:
            conn.rollback()
            cur.close()
            return False, f"Error: {str(e)}"