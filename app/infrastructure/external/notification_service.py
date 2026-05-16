"""
Servicio centralizado de notificaciones.
Cada envío queda registrado en notifi_history como evidencia auditable
(qué se envió, a quién, por qué canal, con qué resultado).
"""
import os
from datetime import datetime, timezone
from typing import Optional, List
from app.infrastructure.logger import app_logger


def _log_attempt(db, user_id, channel, recipient, subject, body, success, error_msg=None):
    from app.domain.models.notification_history import NotificationHistory
    entry = NotificationHistory(
        userId=user_id,
        channel=channel,
        recipient=recipient,
        subject=subject,
        body=body[:500] if body else None,
        success=success,
        error_msg=error_msg,
        date=datetime.now(timezone.utc),
    )
    db.session.add(entry)
    try:
        db.session.commit()
    except Exception:
        db.session.rollback()


class NotificationService:
    """
    Envía notificaciones por FCM (push) y/o email (SendGrid)
    y registra la evidencia en la BD.
    """

    def notify(
        self,
        *,
        user_id: int,
        title: str,
        body: str,
        email: Optional[str] = None,
        fcm_token: Optional[str] = None,
        notif_type: str = "general",
        reference_id: Optional[int] = None,
        reference_type: Optional[str] = None,
        channels: Optional[List[str]] = None,  # ['push', 'email'] — default: ambos
    ) -> dict:
        from app.infrastructure.database import db

        if channels is None:
            channels = ["push", "email"]

        results = {}

        # ── FCM push ────────────────────────────────────────────────────────
        if "push" in channels and fcm_token:
            success, error = True, None
            try:
                from app.infrastructure.external._fcm import send_push
                send_push(fcm_token, title, body, data={
                    'notif_type': notif_type,
                    'reference_id': str(reference_id) if reference_id is not None else '',
                    'reference_type': reference_type or '',
                })
                app_logger.info({"event": "fcm_sent", "user_id": user_id, "title": title})
            except Exception as e:
                success, error = False, str(e)
                app_logger.error({"event": "fcm_error", "user_id": user_id, "details": str(e)})
            _log_attempt(db, user_id, "push", fcm_token, title, body, success, error)
            results["push"] = "ok" if success else f"error: {error}"

        # ── Email (SendGrid) ─────────────────────────────────────────────────
        if "email" in channels and email:
            success, error = True, None
            try:
                from app.infrastructure.external.email_service import SendGridEmailService
                html = f"<h2>{title}</h2><p>{body}</p>"
                SendGridEmailService().send_email(email, title, html)
            except Exception as e:
                success, error = False, str(e)
                app_logger.error({"event": "email_error", "user_id": user_id, "details": str(e)})
            _log_attempt(db, user_id, "email", email, title, body, success, error)
            results["email"] = "ok" if success else f"error: {error}"

        # ── Persistir en tabla notification ──────────────────────────────────
        try:
            from app.domain.models.notification import Notification
            notif = Notification(
                message=body,
                title=title,
                channel=",".join(channels),
                notifType=notif_type,
                userId=user_id,
                referenceId=reference_id,
                referenceType=reference_type,
                status="sent" if results else "pending",
            )
            db.session.add(notif)
            db.session.commit()
        except Exception:
            db.session.rollback()

        return results

    def notify_user_from_id(self, user_id: int, title: str, body: str,
                             notif_type: str = "general", **kwargs) -> dict:
        """Carga email y fcm_token del usuario y envía."""
        from app.domain.models.user import User
        user = User.query.get(user_id)
        if not user:
            return {}
        return self.notify(
            user_id=user_id,
            title=title,
            body=body,
            email=user.email if user.verified else None,
            fcm_token=user.fcmToken,
            notif_type=notif_type,
            **kwargs,
        )


notification_service = NotificationService()
