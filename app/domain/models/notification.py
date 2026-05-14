from app.infrastructure.database import db

class Notification(db.Model):
    __tablename__ = "notification"
    
    idNotification = db.Column('id_notification', db.Integer, primary_key=True, autoincrement=True)
    message = db.Column('message', db.Text)
    createdAt = db.Column('created_at', db.DateTime, default=db.func.current_timestamp())
    channel = db.Column('channel', db.String(50))
