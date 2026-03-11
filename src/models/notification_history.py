from src.database import db
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema 
from marshmallow import fields

class NotificationHistory(db.Model):
    __tablename__ = "NOTIFICATION_HISTORY"
    
    historyId = db.Column(db.Integer, primary_key=True, autoincrement=True)
    status = db.Column(db.String(1), nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    channel = db.Column(db.String(20), nullable=False)
    message = db.Column(db.String(200), nullable=False)
    errorCode = db.Column(db.Integer, nullable=False)
    notificationId = db.Column(db.Integer, db.ForeignKey('NOTIFICATION.notificationId'), nullable=False)
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
