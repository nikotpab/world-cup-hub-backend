from app.infrastructure.database import db

class Phase(db.Model):
    __tablename__ = "phase"
    
    idPhase = db.Column('id_phase', db.Integer, primary_key=True, autoincrement=True)
    phaseName = db.Column('phase_name', db.String(50))
    matchId = db.Column('match_id', db.Integer, db.ForeignKey('match.idmatch'))
    
    match = db.relationship('Match', backref='phases')
