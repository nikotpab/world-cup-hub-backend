from src.database import db
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema 
from marshmallow import fields

class NationalTeam(db.Model):
    __tablename__ = "NATIONAL_TEAM"
    
    nationalTeamId = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    group = db.Column(db.String(1), nullable=False)
    flagUrl = db.Column(db.String(2048), nullable=False)
    
    def create(self):
        db.session.add(self)
        db.session.commit()
        return self

class NationalTeamSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = NationalTeam
        load_instance = True  
        sqla_session = db.session
