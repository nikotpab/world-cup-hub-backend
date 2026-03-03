from src.database import db
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema 
from marshmallow import fields



class Lamina(db.Model):
    __tablename__ = "LAMINA"
    
    IdLamina = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Categoria = db.Column(db.String(20), nullable=False)
    Nombre = db.Column(db.String(50), nullable=False)
    Rareza = db.Column(db.String(1), nullable=False)
    Equipo = db.Column(db.String(20), nullable=False)
    
    def create(self):
        db.session.add(self)
        db.session.commit()
        return self


class LaminaSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Lamina
        load_instance = True  
        sqla_session = db.session

