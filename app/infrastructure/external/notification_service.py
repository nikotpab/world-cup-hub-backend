"""
Servicio centralizado de notificaciones.
Cada envío queda registrado en notifi_history como evidencia auditable
(qué se envió, a quién, por qué canal, con qué resultado).
"""
import os
from datetime import datetime, timezone
from typing import Optional, List
from app.infrastructure.logger import app_logger


def _log_attempt(db, user_id, channel, recipient, subject, body, success,
                 error_msg=None, notif_type=None, reference_id=None, reference_type=None):
    from app.domain.models.notification_history import NotificationHistory
    entry = NotificationHistory(
        userId=user_id,
        channel=channel,
        recipient=recipient,
        subject=subject,
        body=body[:500] if body else None,
        success=success,
        error_msg=error_msg,
        notifType=notif_type,
        referenceId=reference_id,
        referenceType=reference_type,
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

    def _send_push(self, db, user_id, fcm_token, title, body,
                   notif_type, reference_id, reference_type) -> str:
        success, error = True, None
        try:
            from app.infrastructure.external._fcm import send_push
            send_push(fcm_token, title, body, data={
                'notif_type':     notif_type,
                'reference_id':   str(reference_id) if reference_id is not None else '',
                'reference_type': reference_type or '',
            })
            app_logger.info({"event": "fcm_sent", "user_id": user_id, "title": title})
        except Exception as e:
            success, error = False, str(e)
            app_logger.error({"event": "fcm_error", "user_id": user_id, "details": str(e)})
        _log_attempt(db, user_id, "push", fcm_token, title, body, success, error,
                     notif_type=notif_type, reference_id=reference_id, reference_type=reference_type)
        return "ok" if success else f"error: {error}"

    @staticmethod
    def _build_email_html(title: str, body: str) -> str:
        return f"""<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title}</title>
</head>
<body style="margin:0;padding:0;background:#F4F4F0;font-family:'Helvetica Neue',Arial,sans-serif;">
  <table width="100%" cellpadding="0" cellspacing="0" style="background:#F4F4F0;padding:40px 16px;">
    <tr>
      <td align="center">
        <table width="560" cellpadding="0" cellspacing="0" style="max-width:560px;width:100%;">

          <!-- Header -->
          <tr>
            <td style="background:#00341C;padding:32px 40px 24px;">
              <p style="margin:0;font-size:11px;font-weight:700;letter-spacing:3px;color:#CCFF00;text-transform:uppercase;">World Cup Hub</p>
              <h1 style="margin:12px 0 0;font-size:28px;font-weight:900;color:#FFFFFF;letter-spacing:-1px;line-height:1.1;">{title}</h1>
            </td>
          </tr>

          <!-- Body -->
          <tr>
            <td style="background:#FFFFFF;padding:32px 40px;border-left:2px solid #00341C;border-right:2px solid #00341C;">
              <p style="margin:0;font-size:16px;line-height:1.7;color:#1A1A1A;">{body}</p>
            </td>
          </tr>

          <!-- Footer -->
          <tr>
            <td style="background:#00341C;padding:20px 40px;border-top:4px solid #CCFF00;">
              <p style="margin:0;font-size:11px;color:#CCFF00;letter-spacing:2px;font-weight:700;">WORLD CUP HUB &mdash; 2026</p>
              <p style="margin:6px 0 0;font-size:11px;color:#FFFFFF;opacity:0.7;">Este correo fue generado automaticamente. No respondas a este mensaje.</p>
            </td>
          </tr>

        </table>
      </td>
    </tr>
  </table>
</body>
</html>"""

    def _send_email(self, db, user_id, email, title, body,
                    notif_type, reference_id, reference_type) -> str:
        success, error = True, None
        try:
            from app.infrastructure.external.email_service import SmtpEmailService
            SmtpEmailService().send_email(email, title, self._build_email_html(title, body))
        except Exception as e:
            success, error = False, str(e)
            app_logger.error({"event": "email_error", "user_id": user_id, "details": str(e)})
        _log_attempt(db, user_id, "email", email, title, body, success, error,
                     notif_type=notif_type, reference_id=reference_id, reference_type=reference_type)
        return "ok" if success else f"error: {error}"

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
        channels: Optional[List[str]] = None,
    ) -> dict:
        from app.infrastructure.database import db

        if channels is None:
            channels = ["push", "email"]

        results = {}
        if "push" in channels and fcm_token:
            results["push"] = self._send_push(
                db, user_id, fcm_token, title, body, notif_type, reference_id, reference_type
            )
        if "email" in channels and email:
            results["email"] = self._send_email(
                db, user_id, email, title, body, notif_type, reference_id, reference_type
            )

        try:
            from app.domain.models.notification import Notification
            db.session.add(Notification(
                message=body, title=title, channel=",".join(channels),
                notifType=notif_type, userId=user_id,
                referenceId=reference_id, referenceType=reference_type,
                status="sent" if results else "pending",
            ))
            db.session.commit()
        except Exception:
            db.session.rollback()

        return results

    def notify_user_from_id(self, user_id: int, title: str, body: str,
                             notif_type: str = "general", **kwargs) -> dict:
        """Carga email y fcm_token del usuario y envía respetando sus preferencias."""
        from app.domain.models.user import User
        user = User.query.get(user_id)
        if not user:
            return {}

        prefs = user.preferences or {}
        channels = []
        if prefs.get("notif_push", True):
            channels.append("push")
        if prefs.get("notif_email", True) and user.verified:
            channels.append("email")

        if not channels:
            return {}

        return self.notify(
            user_id=user_id,
            title=title,
            body=body,
            email=user.email if user.verified else None,
            fcm_token=user.fcmToken,
            notif_type=notif_type,
            channels=channels,
            **kwargs,
        )

    def broadcast_to_topic(self, topic: str, data: dict = None, title: str = None, body: str = None) -> None:
        """Envía un mensaje FCM a un tema (topic)."""
        try:
            from app.infrastructure.external._fcm import send_to_topic
            send_to_topic(topic, data=data, title=title, body=body)
        except Exception as e:
            app_logger.warning({"event": "fcm_topic_broadcast_failed", "topic": topic, "details": str(e)})


notification_service = NotificationService()
