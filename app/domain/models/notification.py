from app.infrastructure.database import db

class Notification(db.Model):
    __tablename__ = "notification"

    idNotification = db.Column('id_notification', db.Integer, primary_key=True, autoincrement=True)
    message        = db.Column('message', db.Text)
    title          = db.Column('title', db.String(200))
    channel        = db.Column('channel', db.String(50))
    notifType      = db.Column('notif_type', db.String(50), default='general')
    status         = db.Column('status', db.String(20), default='sent')
    userId         = db.Column('user_id', db.Integer, db.ForeignKey('USER.iduser'), nullable=True)
    referenceId    = db.Column('reference_id', db.Integer, nullable=True)
    referenceType  = db.Column('reference_type', db.String(50), nullable=True)
    createdAt      = db.Column('created_at', db.DateTime, default=db.func.current_timestamp())
