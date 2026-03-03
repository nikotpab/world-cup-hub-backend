from src.database import db
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema 
from marshmallow import fields



class Evento(db.Model):
    __tablename__ = "EVENTO"
    
    IdEvento = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Tipo = db.Column(db.String(1), nullable=False)
    Descripcion = db.Column(db.String(200), nullable=False)
    
    def create(self):
        db.session.add(self)
        db.session.commit()
        return self


class EventoSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Evento
        load_instance = True  
        sqla_session = db.session

