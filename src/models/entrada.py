from src.database import db
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema 
from marshmallow import fields



class Entrada(db.Model):
    __tablename__ = "ENTRADA"
    
    IdEntrada = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Estado = db.Column(db.String(1), nullable=False)
    FechaReserva = db.Column(db.DateTime, nullable=False)
    FechaExpiracion = db.Column(db.DateTime, nullable=False)
    Precio = db.Column(db.Float, nullable=False)

    
    def create(self):
        db.session.add(self)
        db.session.commit()
        return self


class EntradaSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Entrada
        load_instance = True  
        sqla_session = db.session

