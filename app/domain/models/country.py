from app.infrastructure.database import db

class Country(db.Model):
    __tablename__ = "COUNTRY"
    
    countryId = db.Column('country_id', db.Integer, primary_key=True, autoincrement=True)
    countryName = db.Column('country_name', db.String(100), nullable=False)
    cities = db.relationship('City', backref='country')
        db.session.add(self)
        db.session.commit()
        return self
