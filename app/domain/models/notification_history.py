from app.infrastructure.database import db

class NotificationHistory(db.Model):
    __tablename__ = "notifi_history"
    
    idNotificationHistory = db.Column('notification_history_id', db.Integer, primary_key=True, autoincrement=True)
    paymentChannel = db.Column('payment_channel', db.String(100))
    date = db.Column('date', db.DateTime, default=db.func.current_timestamp())
    status = db.Column('status', db.String(50))
    notificationId = db.Column('notification_id', db.Integer, db.ForeignKey('notification.id_notification'))
    
    notification = db.relationship('Notification', backref='history')
