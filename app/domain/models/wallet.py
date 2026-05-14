from app.infrastructure.database import db

class Wallet(db.Model):
    __tablename__ = "wallet"
    
    idWallet = db.Column('id_wallet', db.Integer, primary_key=True, autoincrement=True)
    balance = db.Column('balance', db.Numeric(10, 2), default=0)
    idUser = db.Column('id_user', db.Integer, db.ForeignKey('USER.iduser'), unique=True, nullable=False)
    
    user = db.relationship('User', backref='wallets')

    def save(self):
        db.session.add(self)
        db.session.commit()
        return self
