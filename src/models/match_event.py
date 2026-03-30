from src.database import db
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema 
from marshmallow import fields

class MatchEvent(db.Model):
    __tablename__ = "MATCH_EVENT"
    
    eventId = db.Column('match_event_id', db.Integer, primary_key=True, autoincrement=True)
    type = db.Column('type', db.String(50), nullable=False)
    description = db.Column('description', db.String(200), nullable=False)
    minute = db.Column('minute', db.DateTime, nullable=False)
    matchId = db.Column('MATCH_match_id', db.Integer, db.ForeignKey('MATCH.match_id'), nullable=False)
    match = db.relationship('Match', backref='events')
    
    def create(self):
        db.session.add(self)
        db.session.commit()
        return self

class MatchEventSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = MatchEvent
        load_instance = True  
        sqla_session = db.session
