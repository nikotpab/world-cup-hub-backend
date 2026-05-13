import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from app.infrastructure.logger import app_logger

class SendGridEmailService:
    def __init__(self):
        self.api_key = os.environ.get('SENDGRID_API_KEY')
        self.from_email = os.environ.get('SENDGRID_FROM_EMAIL', 'no-reply@mundial2026hub.com')
        if not self.api_key:
            app_logger.warning({"event": "sendgrid_init_warning", "message": "SENDGRID_API_KEY no configurado. Simulando envíos de correo."})

    def send_email(self, to_email: str, subject: str, html_content: str):
        if not self.api_key:
            app_logger.info({"event": "email_simulated", "to": to_email, "subject": subject})
            return {"status": "simulated", "message": "Email simulated (SendGrid not configured)"}

        message = Mail(
            from_email=self.from_email,
            to_emails=to_email,
            subject=subject,
            html_content=html_content)
        
        try:
            sg = SendGridAPIClient(self.api_key)
            response = sg.send(message)
            app_logger.info({"event": "email_sent", "to": to_email, "status_code": response.status_code})
            return {"status": "success", "status_code": response.status_code}
        except Exception as e:
            app_logger.error({"event": "email_send_error", "details": str(e)})
            raise ValueError(f"Error al enviar email transaccional: {str(e)}")
