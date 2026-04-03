from app.infrastructure.database import db

class Stadium(db.Model):
    __tablename__ = "STADIUM"
    
    stadiumId = db.Column('stadium_id', db.Integer, primary_key=True, autoincrement=True)
    city = db.Column('cyty', db.String(200), nullable=False)
    name = db.Column('name', db.String(200), nullable=False)
    country = db.Column('country', db.String(200), nullable=False)
    capacity = db.Column('capacity', db.Integer, nullable=False)
    cityId = db.Column('CITY_city_id', db.Integer, db.ForeignKey('CITY.city_id'), nullable=False)
    cityRel = db.relationship('City', backref='stadiums')
        db.session.add(self)
        db.session.commit()
        return self
