from flask_sqlalchemy import SQLAlchemy
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema 
from marshmallow import fields

db = SQLAlchemy()


class Usuario(db.Model):
    __tablename__ = "USUARIO"
    
    IdUsuario = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Identificacion = db.Column(db.Integer, nullable=False)
    Contrasenia = db.Column(db.String(20), nullable=False)
    Nombre = db.Column(db.String(20), nullable=False)
    Apellido = db.Column(db.String(20), nullable=False)
    Email = db.Column(db.String(30), nullable=False)
    FechaRegistro = db.Column(db.DateTime, nullable=False)
    
    def create(self):
        db.session.add(self)
        db.session.commit()
        return self


class UsuarioSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Usuario
        load_instance = True  
        sqla_session = db.session

