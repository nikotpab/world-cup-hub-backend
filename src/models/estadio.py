from src.database import db
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema 
from marshmallow import fields



class Estadio(db.Model):
    __tablename__ = "ESTADIO"
    
    IdEstadio = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Ciudad = db.Column(db.String(50), nullable=False)
    Nombre = db.Column(db.String(50), nullable=False)
    Pais = db.Column(db.String(50), nullable=False)
    Capacidad = db.Column(db.Integer, nullable=False)
    
    def create(self):
        db.session.add(self)
        db.session.commit()
        return self


class EstadioSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Estadio
        load_instance = True  
        sqla_session = db.session

