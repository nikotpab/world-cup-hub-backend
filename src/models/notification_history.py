from src.database import db
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema 
from marshmallow import fields

class NotificationHistory(db.Model):
    __tablename__ = "NOTIFI_HISTORY"
    
    historyId = db.Column('notification_history_id', db.Integer, primary_key=True, autoincrement=True)
    status = db.Column('status', db.String(50), nullable=False)
    date = db.Column('date', db.DateTime, nullable=False)
    channel = db.Column('payment_channel', db.String(50), nullable=False)
    notificationId = db.Column('NOTIFICATION_notification_id', db.Integer, db.ForeignKey('NOTIFICATION.notification_id'), nullable=False)
    notification = db.relationship('Notification', backref='history')
    
    def create(self):
        db.session.add(self)
        db.session.commit()
        return self

class NotificationHistorySchema(SQLAlchemyAutoSchema):
    class Meta:
        model = NotificationHistory
        load_instance = True  
        sqla_session = db.session
