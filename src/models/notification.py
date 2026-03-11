from src.database import db
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema 
from marshmallow import fields

class Notification(db.Model):
    __tablename__ = "NOTIFICATION"
    
    notificationId = db.Column(db.Integer, primary_key=True, autoincrement=True)
    messageType = db.Column(db.String(30), nullable=False)
    userId = db.Column(db.Integer, db.ForeignKey('USER.userId'), nullable=False)
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
