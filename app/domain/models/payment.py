from app.infrastructure.database import db

class Payment(db.Model):
    __tablename__ = "payment"
    
    idPayment = db.Column('id_payment', db.Integer, primary_key=True, autoincrement=True)
    status = db.Column('status', db.String(50))
    amount = db.Column('amount', db.Numeric(10, 2))
    paymentDate = db.Column('payment_date', db.DateTime, default=db.func.current_timestamp())
    provider = db.Column('provider', db.String(100))
    idUser = db.Column('id_user', db.Integer, db.ForeignKey('USER.iduser'))
    
    user = db.relationship('User', backref='payments')

    def save(self):
        db.session.add(self)
        db.session.commit()
        return self
