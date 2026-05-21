from app.infrastructure.database import db

class MatchStatus(db.Model):
    __tablename__ = "match_status"
    
    idMatchStatus = db.Column('id_match_status', db.Integer, primary_key=True, autoincrement=True)
    nameStatus = db.Column('name_status', db.String(50))
    matchId = db.Column('match_id', db.Integer, db.ForeignKey('match.idmatch'))
    
    match = db.relationship('Match', backref='match_statuses')
