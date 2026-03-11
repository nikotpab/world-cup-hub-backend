from src.database import db
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema 
from marshmallow import fields

class Wallet(db.Model):
    __tablename__ = "WALLET"
    
    walletId = db.Column(db.Integer, primary_key=True, autoincrement=True)
    balance = db.Column(db.Float, nullable=False)
    userId = db.Column(db.Integer, db.ForeignKey('USER.userId'), nullable=False)
    user = db.relationship('User', backref='wallets')
    
    def create(self):
        db.session.add(self)
        db.session.commit()
        return self

class WalletSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Wallet
        load_instance = True  
        sqla_session = db.session
