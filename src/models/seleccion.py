from flask_sqlalchemy import SQLAlchemy
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema 
from marshmallow import fields

db = SQLAlchemy()


class Seleccion(db.Model):
    __tablename__ = "SELECCION"
    
    IdSeleccion = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Nombre = db.Column(db.String(100), nullable=False)
    Grupo = db.Column(db.String(1), nullable=False)
    UrlBandera = db.Column(db.String(2048), nullable=False)
    
    def create(self):
        db.session.add(self)
        db.session.commit()
        return self


class SeleccionSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Seleccion
        load_instance = True  
        sqla_session = db.session

