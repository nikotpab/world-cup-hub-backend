from app.infrastructure.database import db

class NotificationHistory(db.Model):
    __tablename__ = "NOTIFI_HISTORY"
    
    historyId = db.Column('notification_history_id', db.Integer, primary_key=True, autoincrement=True)
    status = db.Column('status', db.String(50), nullable=False)
    date = db.Column('date', db.DateTime, nullable=False)
    channel = db.Column('payment_channel', db.String(50), nullable=False)
    notificationId = db.Column('NOTIFICATION_notification_id', db.Integer, db.ForeignKey('NOTIFICATION.notification_id'), nullable=False)
    notification = db.relationship('Notification', backref='history')
        db.session.add(self)
        db.session.commit()
        return self
