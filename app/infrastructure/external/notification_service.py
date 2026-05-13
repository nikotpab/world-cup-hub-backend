import os
import firebase_admin
from firebase_admin import credentials, messaging
from app.infrastructure.logger import app_logger

class FCMNotificationService:
    def __init__(self):
        self._initialized = False
        try:
            cred_path = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')
            if cred_path and os.path.exists(cred_path):
                cred = credentials.Certificate(cred_path)
                firebase_admin.initialize_app(cred)
                self._initialized = True
            else:
                app_logger.warning({"event": "fcm_init_warning", "message": "No se encontraron credenciales de Firebase. Simulando notificaciones."})
        except Exception as e:
             app_logger.error({"event": "fcm_init_error", "details": str(e)})

    def send_push_notification(self, token: str, title: str, body: str, data: dict = None):
        if not self._initialized:
            app_logger.info({"event": "fcm_notification_simulated", "token": token, "title": title})
            return {"status": "simulated", "message": "Notification simulated (FCM not configured)"}

        try:
            message = messaging.Message(
                notification=messaging.Notification(
                    title=title,
                    body=body,
                ),
                data=data or {},
                token=token,
            )
            response = messaging.send(message)
            app_logger.info({"event": "fcm_notification_sent", "response": response})
            return {"status": "success", "response": response}
        except Exception as e:
            app_logger.error({"event": "fcm_send_error", "details": str(e)})
            raise ValueError(f"Error al enviar notificación push: {str(e)}")
