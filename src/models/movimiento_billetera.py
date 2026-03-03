from src.database import db
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema 
from marshmallow import fields



class MovimientoBilletera(db.Model):
    __tablename__ = "MOVIMIENTO_BILLETERA"
    
    IdMovimiento = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Monto = db.Column(db.Float, nullable=False)
    Fecha = db.Column(db.DateTime, nullable=False)
    Tipo = db.Column(db.String(10), nullable=False)
    Motivo = db.Column(db.String(200), nullable=False)

    
    def create(self):
        db.session.add(self)
        db.session.commit()
        return self


class MovimientoBilleteraSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = MovimientoBilletera
        load_instance = True  
        sqla_session = db.session

