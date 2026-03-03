from src.database import db
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema 
from marshmallow import fields



class EventoPartido(db.Model):
    __tablename__ = "EVENTO_PARTIDO"
    
    IdEvento = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Tipo = db.Column(db.String(1), nullable=False)
    Descripcion = db.Column(db.String(200), nullable=False)
    Minuto = db.Column(db.String(10), nullable=False)

    
    def create(self):
        db.session.add(self)
        db.session.commit()
        return self


class EventoPartidoSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = EventoPartido
        load_instance = True  
        sqla_session = db.session

