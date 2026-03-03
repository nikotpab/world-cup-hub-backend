from src.database import db
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema 
from marshmallow import fields



class HistorialNotificacion(db.Model):
    __tablename__ = "HISTORAL_NOTIFICACION"
    
    IdHistorialNot = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Estado = db.Column(db.String(1), nullable=False)
    Fecha = db.Column(db.DateTime, nullable=False)
    Canal = db.Column(db.String(20), nullable=False)
    Mensaje = db.Column(db.String(200), nullable=False)
    CodigoError = db.Column(db.Integer, nullable=False)

    
    def create(self):
        db.session.add(self)
        db.session.commit()
        return self


class HistorialNotificacionSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = HistorialNotificacion
        load_instance = True  
        sqla_session = db.session

