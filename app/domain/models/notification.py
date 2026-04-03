from app.infrastructure.database import db

class Notification(db.Model):
    __tablename__ = "NOTIFICATION"
    
    notificationId = db.Column('notification_id', db.Integer, primary_key=True, autoincrement=True)
    messageType = db.Column('message_type', db.String(50), nullable=False)
    userId = db.Column('USER_user_id', db.Integer, db.ForeignKey('USER.user_id'), nullable=False)
    message = db.Column('message', db.String(500), nullable=False)
    user = db.relationship('User', backref='notifications')
        db.session.add(self)
        db.session.commit()
        return self
