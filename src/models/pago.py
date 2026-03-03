from src.database import db
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema 
from marshmallow import fields



class Pago(db.Model):
    __tablename__ = "PAGO"
    
    IdPago = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Estado = db.Column(db.String(1), nullable=False)
    Fecha = db.Column(db.DateTime, nullable=False)
    Monto = db.Column(db.Float, nullable=False)
    Proveedor = db.Column(db.String(50), nullable=False)

    
    def create(self):
        db.session.add(self)
        db.session.commit()
        return self


class PagoSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Pago
        load_instance = True  
        sqla_session = db.session

