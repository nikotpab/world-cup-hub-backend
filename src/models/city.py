from src.database import db
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema

class City(db.Model):
    __tablename__ = "CITY"
    
    cityId = db.Column('city_id', db.Integer, primary_key=True, autoincrement=True)
    cityName = db.Column('city_name', db.String(100), nullable=False)
    countryId = db.Column('COUNTRY_country_id', db.Integer, db.ForeignKey('COUNTRY.country_id'), nullable=False)
    
    def create(self):
        db.session.add(self)
        db.session.commit()
        return self

class CitySchema(SQLAlchemyAutoSchema):
    class Meta:
        model = City
        load_instance = True
        sqla_session = db.session
