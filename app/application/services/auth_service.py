from typing import Dict, Any
from app.application.interfaces.user_repository import IUserRepository
from passlib.hash import argon2

class AuthService:
    def __init__(self, user_repository: IUserRepository):
        self.user_repository = user_repository

    def login(self, data: dict) -> Dict[str, Any]:
        email = data.get("email")
        password = data.get("password")
        
        if not email or not password:
            raise ValueError("Email and password are required")
            
        users = self.user_repository.get_all()
        user = next((u for u in users if u.email == email), None)
        
        if not user:
            raise ValueError("Invalid email or password")
            
        # Simplificación para el demo. En prod usar argon2.verify(password, user.password)
        if user.password != password:
            raise ValueError("Invalid email or password")
            
        return {
            "token": "fake-jwt-token-12345", # Para propósitos del demo
            "user": {
                "userId": user.userId,
                "email": user.email,
                "firstName": user.firstName,
                "lastName": user.lastName,
                "roleId": user.roleId
            }
        }
