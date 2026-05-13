from app.infrastructure.database import db

class Transfer(db.Model):
    __tablename__ = "TRANFER"
    
    transferId = db.Column('transfer_id', db.Integer, primary_key=True, autoincrement=True)
    date = db.Column('date', db.DateTime, nullable=False)
    userId = db.Column('USER_user_id', db.Integer, db.ForeignKey('USER.user_id'), nullable=False)
    user = db.relationship('User', backref='transfers')

    def save(self):
        db.session.add(self)
        db.session.commit()
        return self
