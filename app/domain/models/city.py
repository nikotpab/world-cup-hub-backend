from app.infrastructure.database import db

class City(db.Model):
    __tablename__ = "CITY"
    
    cityId = db.Column('city_id', db.Integer, primary_key=True, autoincrement=True)
    cityName = db.Column('city_name', db.String(100), nullable=False)
    countryId = db.Column('COUNTRY_country_id', db.Integer, db.ForeignKey('COUNTRY.country_id'), nullable=False)

    def save(self):
        db.session.add(self)
        db.session.commit()
        return self
