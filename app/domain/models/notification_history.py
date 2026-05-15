from app.infrastructure.database import db

class NotificationHistory(db.Model):
    __tablename__ = "notifi_history"

    idHistory  = db.Column('notification_history_id', db.Integer, primary_key=True, autoincrement=True)
    userId     = db.Column('user_id', db.Integer, nullable=True)
    channel    = db.Column('channel', db.String(50))
    recipient  = db.Column('recipient', db.String(300))
    subject    = db.Column('subject', db.String(200))
    body       = db.Column('body', db.Text)
    success    = db.Column('success', db.Boolean, default=True)
    error_msg  = db.Column('error_msg', db.Text, nullable=True)
    date       = db.Column('date', db.DateTime, default=db.func.current_timestamp())
