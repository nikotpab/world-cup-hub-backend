from flask_sqlalchemy import SQLAlchemy
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema 
from marshmallow import fields

db = SQLAlchemy()


class Partido(db.Model):
    __tablename__ = "PARTIDO"
    
    IdPartido = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Estado = db.Column(db.String(50), nullable=False)
    Fase = db.Column(db.String(1), nullable=False)
    Fecha_hora = db.Column(db.DateTime, nullable=False)
    
    def create(self):
        db.session.add(self)
        db.session.commit()
        return self


class PartidoSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Partido
        load_instance = True  
        sqla_session = db.session

