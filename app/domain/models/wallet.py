from app.infrastructure.database import db

class Wallet(db.Model):
    __tablename__ = "WALLET"
    
    walletId = db.Column('wallet_id', db.Integer, primary_key=True)
    balance = db.Column('balance', db.Float, nullable=True)
    userId = db.Column('USER_user_id', db.Integer, db.ForeignKey('USER.user_id'), primary_key=True, nullable=False)
    user = db.relationship('User', backref='wallets')

    def save(self):
        db.session.add(self)
        db.session.commit()
        return self
