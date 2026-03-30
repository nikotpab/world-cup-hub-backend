from src.database import db
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema 
from marshmallow import fields

class Notification(db.Model):
    __tablename__ = "NOTIFICATION"
    
    notificationId = db.Column('notification_id', db.Integer, primary_key=True, autoincrement=True)
    messageType = db.Column('message_type', db.String(50), nullable=False)
    userId = db.Column('USER_user_id', db.Integer, db.ForeignKey('USER.user_id'), nullable=False)
    message = db.Column('message', db.String(500), nullable=False)
    user = db.relationship('User', backref='notifications')
    
    def create(self):
        db.session.add(self)
        db.session.commit()
        return self

class NotificationSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Notification
        load_instance = True  
        sqla_session = db.session
