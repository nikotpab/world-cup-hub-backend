from src.database import db
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema 
from marshmallow import fields



class Notifiacion(db.Model):
    __tablename__ = "NOTIFICACION"
    
    IdNotifiacion = db.Column(db.Integer, primary_key=True, autoincrement=True)
    TipoMensaje = db.Column(db.String(30), nullable=False)
    
    def create(self):
        db.session.add(self)
        db.session.commit()
        return self


class NotifiacionSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Notifiacion
        load_instance = True  
        sqla_session = db.session

