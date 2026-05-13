import smtplib
import random
import string
import jwt
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Any
from app.application.interfaces.user_repository import IUserRepository
from passlib.hash import argon2
from datetime import datetime, timedelta
from flask import current_app

class AuthService:
    def __init__(self, user_repository: IUserRepository):
        self.user_repository = user_repository

    def _generate_verification_code(self) -> str:
        return ''.join(random.choices(string.digits, k=6))

    def _send_verification_email(self, email: str, code: str):
        smtp_server = os.environ.get('SMTP_SERVER', 'smtp.hostinger.com')
        smtp_port = int(os.environ.get('SMTP_PORT', 465))
        sender_email = os.environ.get('SMTP_EMAIL', 'informacion@worldcuphub.online')
        sender_password = os.environ.get('SMTP_PASSWORD')

        if not sender_password:
            from app.infrastructure.logger import app_logger
            app_logger.warning({"event": "smtp_missing_password", "message": "SMTP_PASSWORD no configurado. Simulando envío."})
            return

        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = email
        msg['Subject'] = "Verifica tu cuenta - Mundial 2026 Hub"

        body = f"""
        <html>
            <body>
                <h2>Bienvenido a Mundial 2026 Hub</h2>
                <p>Tu código de verificación es: <strong>{code}</strong></p>
                <p>Por favor, ingresa este código en la aplicación para activar tu cuenta.</p>
            </body>
        </html>
        """
        msg.attach(MIMEText(body, 'html'))

        try:
            with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:
                server.login(sender_email, sender_password)
                server.send_message(msg)
        except Exception as e:
            from app.infrastructure.logger import app_logger
            app_logger.error({"event": "email_verification_error", "details": str(e)})

    def register(self, data: dict) -> Dict[str, Any]:
        email = data.get("email")
        password = data.get("password")
        first_name = data.get("firstName")
        last_name = data.get("lastName")

        if not all([email, password, first_name, last_name]):
            raise ValueError("Faltan campos requeridos")

        existing_user = self.user_repository.get_by_email(email)
        if existing_user:
            raise ValueError("El correo ya está registrado")

        hashed_password = argon2.hash(password)
        verification_code = self._generate_verification_code()

        user_data = {
            "email": email,
            "password": hashed_password,
            "firstName": first_name,
            "lastName": last_name,
            "verified": False,
            "verificationCode": verification_code,
            "roleId": 2  # Asumiendo rol de aficionado por defecto
        }

        saved_user = self.user_repository.save(user_data)
        self._send_verification_email(email, verification_code)

        return {
            "success": True,
            "message": "Usuario registrado. Revisa tu correo para el código de verificación."
        }

    def verify_email(self, data: dict) -> Dict[str, Any]:
        email = data.get("email")
        code = data.get("code")

        if not email or not code:
            raise ValueError("Email and code are required")

        user = self.user_repository.get_by_email(email)
        if not user:
            raise ValueError("Usuario no encontrado")

        if user.get("verified"):
            raise ValueError("El usuario ya está verificado")

        if user.get("verificationCode") != code:
            raise ValueError("Código de verificación inválido")

        # Update user
        user["verified"] = True
        user["verificationCode"] = None
        self.user_repository.save(user)

        return {"success": True, "message": "Cuenta verificada con éxito"}

    def login(self, data: dict) -> Dict[str, Any]:
        email = data.get("email")
        password = data.get("password")
        
        if not email or not password:
            raise ValueError("Email y contraseña requeridos")
            
        user = self.user_repository.get_by_email(email)
        
        if not user:
            raise ValueError("Credenciales inválidas")
            
        try:
            if not argon2.verify(password, user.get("password")):
                raise ValueError("Credenciales inválidas")
        except Exception:
            raise ValueError("Credenciales inválidas")
            
        if not user.get("verified"):
            raise ValueError("Por favor verifica tu correo electrónico antes de iniciar sesión.")
            
        if user.get("accountStatus") != 'activo':
            raise ValueError("Tu cuenta está suspendida.")

        secret_key = current_app.config.get('JWT_SECRET_KEY') or current_app.config.get('SECRET_KEY') or 'secret'
        payload = {
            "userId": user.get("userId"),
            "email": user.get("email"),
            "roleId": user.get("roleId"),
            "exp": datetime.utcnow() + timedelta(hours=24)
        }
        token = jwt.encode(payload, secret_key, algorithm="HS256")
            
        return {
            "token": token,
            "user": {
                "userId": user.get("userId"),
                "email": user.get("email"),
                "firstName": user.get("firstName"),
                "lastName": user.get("lastName"),
                "roleId": user.get("roleId")
            }
        }
