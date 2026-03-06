from src.database import db
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema 
from marshmallow import fields

class Payment(db.Model):
    __tablename__ = "PAYMENT"
    
    paymentId = db.Column(db.Integer, primary_key=True, autoincrement=True)
    status = db.Column(db.String(1), nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    amount = db.Column(db.Float, nullable=False)
    provider = db.Column(db.String(50), nullable=False)
    
    def create(self):
        db.session.add(self)
        db.session.commit()
        return self

class PaymentSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Payment
        load_instance = True  
        sqla_session = db.session
