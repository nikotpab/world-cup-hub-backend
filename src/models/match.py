from src.database import db
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema 
from marshmallow import fields

class Match(db.Model):
    __tablename__ = "MATCH"
    
    matchId = db.Column(db.Integer, primary_key=True, autoincrement=True)
    status = db.Column(db.String(50), nullable=False)
    phase = db.Column(db.String(1), nullable=False)
    scheduledAt = db.Column(db.DateTime, nullable=False)
    stadiumId = db.Column(db.Integer, db.ForeignKey('STADIUM.stadiumId'), nullable=False)
    stadium = db.relationship('Stadium', backref='matches')
    
    def create(self):
        db.session.add(self)
        db.session.commit()
        return self

class MatchSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Match
        load_instance = True  
        sqla_session = db.session
