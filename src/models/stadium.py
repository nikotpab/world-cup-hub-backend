from src.database import db
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema 
from marshmallow import fields

class Stadium(db.Model):
    __tablename__ = "STADIUM"
    
    stadiumId = db.Column(db.Integer, primary_key=True, autoincrement=True)
    city = db.Column(db.String(50), nullable=False)
    name = db.Column(db.String(50), nullable=False)
    country = db.Column(db.String(50), nullable=False)
    capacity = db.Column(db.Integer, nullable=False)
    
    def create(self):
        db.session.add(self)
        db.session.commit()
        return self

class StadiumSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Stadium
        load_instance = True  
        sqla_session = db.session
