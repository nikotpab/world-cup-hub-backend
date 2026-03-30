from src.database import db
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema 
from marshmallow import fields

class Wallet(db.Model):
    __tablename__ = "WALLET"
    
    walletId = db.Column('wallet_id', db.Integer, primary_key=True)
    balance = db.Column('balance', db.Float, nullable=True)
    userId = db.Column('USER_user_id', db.Integer, db.ForeignKey('USER.user_id'), primary_key=True, nullable=False)
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
