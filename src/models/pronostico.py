from src.database import db
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema 
from marshmallow import fields



class Pronostico(db.Model):
    __tablename__ = "PRONOSTICO"
    
    IdPronostico = db.Column(db.Integer, primary_key=True, autoincrement=True)
    GolesLocal = db.Column(db.Integer, nullable=False)
    GolesVisitante = db.Column(db.Integer, nullable=False)

    
    def create(self):
        db.session.add(self)
        db.session.commit()
        return self


class PronosticoSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Pronostico
        load_instance = True  
        sqla_session = db.session

