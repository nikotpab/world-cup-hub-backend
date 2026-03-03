from src.database import db
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema 
from marshmallow import fields



class GrupoPolla(db.Model):
    __tablename__ = "GRUPO_POLLA"
    
    IdGrupoPolla = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Nombre = db.Column(db.String(30), nullable=False)
    CodigoInvitación = db.Column(db.Integer, nullable=False)

    
    def create(self):
        db.session.add(self)
        db.session.commit()
        return self


class GrupoPollaSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = GrupoPolla
        load_instance = True  
        sqla_session = db.session

