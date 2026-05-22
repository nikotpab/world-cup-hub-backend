import secrets
import uuid
import jwt
import os
from typing import Dict, Any
from app.application.interfaces.user_repository import IUserRepository
from passlib.hash import argon2
from datetime import datetime, timedelta, timezone
from flask import current_app


class _UnverifiedError(ValueError):
    """El usuario existe y la contraseña es correcta, pero el email no fue verificado."""
    def __init__(self, email: str):
        super().__init__("Por favor verifica tu correo electrónico antes de iniciar sesión.")
        self.email = email


class AuthService:
    def __init__(self, user_repository: IUserRepository):
        self.user_repository = user_repository

    def _generate_verification_code(self) -> str:
        return f"{secrets.randbelow(1_000_000):06d}"

    def _send_verification_email(self, email: str, code: str) -> bool:
        from app.infrastructure.external.email_service import SmtpEmailService
        from app.infrastructure.logger import app_logger
        subject = "Verifica tu cuenta - Mundial 2026 Hub"
        body = f"""
        <html>
            <body>
                <h2>Bienvenido a Mundial 2026 Hub</h2>
                <p>Tu código de verificación es: <strong>{code}</strong></p>
                <p>Por favor, ingresa este código en la aplicación para activar tu cuenta.</p>
            </body>
        </html>
        """
        try:
            SmtpEmailService().send_email(email, subject, body)
            return True
        except Exception as e:
            app_logger.error({"event": "email_verification_error", "details": str(e)})
            return False

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
            "roleId": 2
        }

        self.user_repository.save(user_data)
        email_sent = self._send_verification_email(email, verification_code)

        return {
            "success": True,
            "message": "Usuario registrado. Revisa tu correo para el código de verificación.",
            "emailSent": email_sent,
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

        user["verified"] = True
        user["verificationCode"] = None
        self.user_repository.save(user)

        return {"success": True, "message": "Cuenta verificada con éxito"}

    def resend_verification(self, data: dict) -> Dict[str, Any]:
        email = data.get("email")
        if not email:
            raise ValueError("Email requerido")

        user = self.user_repository.get_by_email(email)
        if not user:
            raise ValueError("Usuario no encontrado")
        if user.get("verified"):
            raise ValueError("El usuario ya está verificado")

        new_code = self._generate_verification_code()
        user["verificationCode"] = new_code
        self.user_repository.save(user)
        email_sent = self._send_verification_email(email, new_code)

        return {
            "success": True,
            "message": "Código reenviado. Revisa tu correo." if email_sent else "No se pudo enviar el correo. Verifica la configuración SMTP o usa el endpoint de diagnóstico.",
            "emailSent": email_sent,
        }

    def login(self, data: dict) -> Dict[str, Any]:
        email = data.get("email")
        password = data.get("password")

        if not email or not password:
            raise ValueError("Email y contraseña requeridos")

        user = self.user_repository.get_by_email(email)
        _ERR_INVALID_CREDENTIALS = "Credenciales inválidas"
        if not user:
            raise ValueError(_ERR_INVALID_CREDENTIALS)

        try:
            if not argon2.verify(password, user.get("password")):
                raise ValueError(_ERR_INVALID_CREDENTIALS)
        except Exception:
            raise ValueError(_ERR_INVALID_CREDENTIALS)

        if not user.get("verified"):
            raise _UnverifiedError(email)

        if user.get("accountStatus") != 'activo':
            raise ValueError("Tu cuenta está suspendida.")

        secret_key = current_app.config.get('JWT_SECRET_KEY') or current_app.config.get('SECRET_KEY') or 'secret'
        payload = {
            "jti": str(uuid.uuid4()),
            "userId": user.get("userId"),
            "email": user.get("email"),
            "roleId": user.get("roleId"),
            "exp": datetime.now(timezone.utc) + timedelta(hours=24),
        }
        token = jwt.encode(payload, secret_key, algorithm="HS256")

        return {
            "token": token,
            "user": {
                "userId":         user.get("userId"),
                "email":          user.get("email"),
                "firstName":      user.get("firstName"),
                "lastName":       user.get("lastName"),
                "roleId":         user.get("roleId"),
                "profilePicture": user.get("profilePicture"),
            },
        }
