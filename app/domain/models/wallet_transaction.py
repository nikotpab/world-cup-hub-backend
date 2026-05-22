from app.infrastructure.database import db

class WalletTransaction(db.Model):
    __tablename__ = "wallet_transaction"
    
    idTransaction = db.Column('id_transaction', db.Integer, primary_key=True, autoincrement=True)
    transactionDate = db.Column('transaction_date', db.DateTime, default=db.func.current_timestamp())
    type = db.Column('type', db.String(50))
    amount = db.Column('amount', db.Numeric(10, 2))
    reason = db.Column('reason', db.Text)
    idWallet = db.Column('id_wallet', db.Integer, db.ForeignKey('wallet.id_wallet'))
    
    wallet = db.relationship('Wallet', backref='transactions')

    def save(self):
        db.session.add(self)
        db.session.commit()
        return self
