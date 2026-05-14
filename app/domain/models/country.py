from app.infrastructure.database import db

class Country(db.Model):
    __tablename__ = "country"
    
    countryId = db.Column('idcountry', db.Integer, primary_key=True, autoincrement=True)
    name = db.Column('countryname', db.String(100), nullable=False)
