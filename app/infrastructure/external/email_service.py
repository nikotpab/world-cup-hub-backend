import os
import boto3
from botocore.exceptions import ClientError, NoCredentialsError
from app.infrastructure.logger import app_logger


class SesEmailService:
    """
    Sends transactional email via AWS SES (boto3).
    In production (ECS) credentials come from the task IAM role — no keys needed.
    In local dev boto3 picks up ~/.aws/credentials automatically.
    """

    def __init__(self):
        self.from_email = os.environ.get('SES_FROM_EMAIL', 'informacion@worldcuphub.online')
        self.aws_region = os.environ.get('AWS_DEFAULT_REGION', 'us-east-1')

    def send_email(self, to_email: str, subject: str, html_content: str) -> dict:
        try:
            client = boto3.client('ses', region_name=self.aws_region)
            response = client.send_email(
                Source=self.from_email,
                Destination={'ToAddresses': [to_email]},
                Message={
                    'Subject': {'Data': subject, 'Charset': 'UTF-8'},
                    'Body': {'Html': {'Data': html_content, 'Charset': 'UTF-8'}},
                },
            )
            msg_id = response['MessageId']
            app_logger.info({
                "event": "email_sent",
                "to": to_email,
                "subject": subject,
                "message_id": msg_id,
            })
            return {"status": "success", "message_id": msg_id}

        except NoCredentialsError:
            app_logger.warning({
                "event": "ses_no_credentials",
                "message": "AWS credentials not found. Configure ~/.aws or set AWS_ACCESS_KEY_ID env var.",
                "to": to_email,
            })
            raise ValueError("SES sin credenciales AWS. Configura ~/.aws o AWS_ACCESS_KEY_ID.")

        except ClientError as e:
            code = e.response['Error']['Code']
            msg = e.response['Error']['Message']
            app_logger.error({"event": "ses_send_error", "code": code, "details": msg, "to": to_email})
            raise ValueError(f"Error SES ({code}): {msg}")

        except Exception as e:
            app_logger.error({"event": "ses_send_error", "details": str(e), "to": to_email})
            raise ValueError(f"Error inesperado al enviar email: {e}")


# Aliases — mantienen compatibilidad con imports existentes en auth_service y notification_service
SmtpEmailService = SesEmailService
SendGridEmailService = SesEmailService
