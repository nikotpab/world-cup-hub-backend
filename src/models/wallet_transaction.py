from src.database import db
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema 
from marshmallow import fields

class WalletTransaction(db.Model):
    __tablename__ = "WALLET_TRANSACTION"
    
    transactionId = db.Column('id_wallet_movement', db.Integer, primary_key=True)
    amount = db.Column('amount', db.Float, nullable=False)
    date = db.Column('date', db.DateTime, nullable=False)
    type = db.Column('type', db.String(50), nullable=False)
    reason = db.Column('reason', db.String(4000), nullable=False)
    walletId = db.Column('WALLET_wallet_id', db.Integer, primary_key=True, nullable=False)
    userId = db.Column('WALLET_user_id', db.Integer, db.ForeignKey('USER.user_id'), primary_key=True, nullable=False)
    
    __table_args__ = (
        db.ForeignKeyConstraint(
            ['WALLET_wallet_id', 'WALLET_user_id'],
            ['WALLET.wallet_id', 'WALLET.USER_user_id']
        ),
    )
    
    wallet = db.relationship('Wallet', backref='transactions')
    user = db.relationship('User', backref='wallet_transactions')
    
    def create(self):
        db.session.add(self)
        db.session.commit()
        return self

class WalletTransactionSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = WalletTransaction
        load_instance = True  
        sqla_session = db.session
