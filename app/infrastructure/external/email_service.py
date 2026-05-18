import os
import ssl
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.infrastructure.logger import app_logger


class SmtpEmailService:
    def __init__(self):
        self.smtp_server   = os.environ.get('SMTP_SERVER', 'smtp.hostinger.com')
        self.smtp_port     = int(os.environ.get('SMTP_PORT', '465'))
        self.smtp_email    = os.environ.get('SMTP_EMAIL')
        self.smtp_password = os.environ.get('SMTP_PASSWORD')

        if not self.smtp_email or not self.smtp_password:
            app_logger.warning({
                "event": "smtp_init_warning",
                "message": "SMTP credentials not configured. Simulating email sends.",
            })

    def send_email(self, to_email: str, subject: str, html_content: str):
        if not self.smtp_email or not self.smtp_password:
            app_logger.info({"event": "email_simulated", "to": to_email, "subject": subject})
            return {"status": "simulated", "message": "Email simulated (SMTP not configured)"}

        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"]    = self.smtp_email
        msg["To"]      = to_email
        msg.attach(MIMEText(html_content, "html"))

        try:
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL(self.smtp_server, self.smtp_port, context=context) as server:
                server.login(self.smtp_email, self.smtp_password)
                server.sendmail(self.smtp_email, to_email, msg.as_string())

            app_logger.info({"event": "email_sent", "to": to_email, "subject": subject})
            return {"status": "success"}

        except Exception as e:
            app_logger.error({"event": "email_send_error", "details": str(e)})
            raise ValueError(f"Error al enviar email via SMTP: {str(e)}")


# Alias for backwards compatibility
SendGridEmailService = SmtpEmailService
