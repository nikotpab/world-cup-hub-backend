from src.database import db
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema 
from marshmallow import fields

class WalletTransaction(db.Model):
    __tablename__ = "WALLET_TRANSACTION"
    
    transactionId = db.Column(db.Integer, primary_key=True, autoincrement=True)
    amount = db.Column(db.Float, nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    type = db.Column(db.String(10), nullable=False)
    reason = db.Column(db.String(200), nullable=False)
    
    def create(self):
        db.session.add(self)
        db.session.commit()
        return self

class WalletTransactionSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = WalletTransaction
        load_instance = True  
        sqla_session = db.session
