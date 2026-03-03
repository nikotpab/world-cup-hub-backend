from src.database import db
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema 
from marshmallow import fields



class Transferencia(db.Model):
    __tablename__ = "TRANSFERENCIA"
    
    IdTransferencia = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Fecha = db.Column(db.DateTime, nullable=False)
    
    def create(self):
        db.session.add(self)
        db.session.commit()
        return self


class TransferenciaSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Transferencia
        load_instance = True  
        sqla_session = db.session

