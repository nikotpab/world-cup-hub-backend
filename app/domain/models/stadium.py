from app.infrastructure.database import db

class Stadium(db.Model):
    __tablename__ = "stadium"
    
    stadiumId = db.Column('idstadium', db.Integer, primary_key=True, autoincrement=True)
    name = db.Column('stadiumname', db.String(100), nullable=False)
    capacity = db.Column('capacity', db.Integer, nullable=False)
    cityId = db.Column('idcity', db.Integer, db.ForeignKey('city.idcity'), nullable=True)
    
    city = db.relationship('City', backref='stadiums')
