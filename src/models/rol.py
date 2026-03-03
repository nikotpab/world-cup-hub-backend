from src.database import db
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema 
from marshmallow import fields



class Rol(db.Model):
    __tablename__ = "ROL"
    
    IdRol = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Nombre = db.Column(db.String(30), nullable=False)
    
    def create(self):
        db.session.add(self)
        db.session.commit()
        return self


class RolSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Rol
        load_instance = True  
        sqla_session = db.session

