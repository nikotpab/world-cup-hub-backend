from src.database import db
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema

class Country(db.Model):
    __tablename__ = "COUNTRY"
    
    countryId = db.Column('country_id', db.Integer, primary_key=True, autoincrement=True)
    countryName = db.Column('country_name', db.String(100), nullable=False)
    cities = db.relationship('City', backref='country')
    
    def create(self):
        db.session.add(self)
        db.session.commit()
        return self

class CountrySchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Country
        load_instance = True
        sqla_session = db.session
