from src.database import db
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema 
from marshmallow import fields



class Auditoria(db.Model):
    __tablename__ = "AUDITORIA"
    
    IdAuditoria = db.Column(db.Integer, primary_key=True, autoincrement=True)
    IdCorrelacion = db.Column(db.Integer, nullable=False)
    Resultado = db.Column(db.String(200), nullable=False)
    PayLoad = db.Column(db.String(200), nullable=False)
    EntidadAfectada = db.Column(db.String(30), nullable=False)
    Accion = db.Column(db.String(200), nullable=False)
    FechaHora = db.Column(db.DateTime, nullable=False)
    
    def create(self):
        db.session.add(self)
        db.session.commit()
        return self


class AuditoriaSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Auditoria
        load_instance = True  
        sqla_session = db.session

