from src.database import db
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema 
from marshmallow import fields



class Paquete(db.Model):
    __tablename__ = "PAQUETE"
    
    IdPaquete = db.Column(db.Integer, primary_key=True, autoincrement=True)
    FeachaApertura = db.Column(db.DateTime, nullable=False)
    
    def create(self):
        db.session.add(self)
        db.session.commit()
        return self


class PaqueteSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Paquete
        load_instance = True  
        sqla_session = db.session

