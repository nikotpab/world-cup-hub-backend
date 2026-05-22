from app.infrastructure.database import db

class MatchEvent(db.Model):
    __tablename__ = "match_event"
    
    idEvent = db.Column('id_event', db.Integer, primary_key=True, autoincrement=True)
    eventType = db.Column('event_type', db.String(50))
    minute = db.Column('minute', db.Integer)
    description = db.Column('description', db.Text)
    idMatch = db.Column('id_match', db.Integer, db.ForeignKey('match.idmatch'))
    
    match = db.relationship('Match', backref='events')
