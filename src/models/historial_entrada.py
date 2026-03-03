from src.database import db
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema 
from marshmallow import fields



class HistorialEntrada(db.Model):
    __tablename__ = "HISTORIAL_ENTRADA"
    
    IdHistorial = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Estado = db.Column(db.String(1), nullable=False)
    Motivo = db.Column(db.String(200), nullable=False)
    FechaHoraCambio = db.Column(db.DateTime, nullable=False)

    
    def create(self):
        db.session.add(self)
        db.session.commit()
        return self


class HistorialEntradaSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = HistorialEntrada
        load_instance = True  
        sqla_session = db.session

