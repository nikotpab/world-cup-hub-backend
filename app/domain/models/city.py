from app.infrastructure.database import db

class City(db.Model):
    __tablename__ = "city"
    
    cityId = db.Column('idcity', db.Integer, primary_key=True, autoincrement=True)
    name = db.Column('cityname', db.String(100), nullable=False)
    countryId = db.Column('idcountry', db.Integer, db.ForeignKey('country.idcountry'), nullable=True)
    
    country = db.relationship('Country', backref='cities')
