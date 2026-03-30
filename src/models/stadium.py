from src.database import db
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema 
from marshmallow import fields

class Stadium(db.Model):
    __tablename__ = "STADIUM"
    
    stadiumId = db.Column('stadium_id', db.Integer, primary_key=True, autoincrement=True)
    city = db.Column('cyty', db.String(200), nullable=False)
    name = db.Column('name', db.String(200), nullable=False)
    country = db.Column('country', db.String(200), nullable=False)
    capacity = db.Column('capacity', db.Integer, nullable=False)
    cityId = db.Column('CITY_city_id', db.Integer, db.ForeignKey('CITY.city_id'), nullable=False)
    cityRel = db.relationship('City', backref='stadiums')
    
    def create(self):
        db.session.add(self)
        db.session.commit()
        return self

class StadiumSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Stadium
        load_instance = True  
        sqla_session = db.session
