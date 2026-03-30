from src.database import db
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema 
from marshmallow import fields

class Match(db.Model):
    __tablename__ = "MATCH"
    
    matchId = db.Column('match_id', db.Integer, primary_key=True, autoincrement=True)
    status = db.Column('status', db.String(50), nullable=False)
    phase = db.Column('phase', db.String(50), nullable=False)
    scheduledAt = db.Column('date_hour', db.DateTime, nullable=False)
    stadiumId = db.Column('STADIUM_stadium_id', db.Integer, db.ForeignKey('STADIUM.stadium_id'), nullable=False)
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
