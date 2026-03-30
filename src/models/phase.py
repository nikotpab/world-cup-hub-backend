from src.database import db
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema

class Phase(db.Model):
    __tablename__ = "PHASE"
    
    phaseId = db.Column('id_phase', db.Integer, primary_key=True, autoincrement=True)
    phaseName = db.Column('phase_name', db.String(4000), nullable=False)
    matchId = db.Column('MATCH_match_id', db.Integer, db.ForeignKey('MATCH.match_id'), nullable=False)
    match = db.relationship('Match', backref='phases_rel')
    
    def create(self):
        db.session.add(self)
        db.session.commit()
        return self

class PhaseSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Phase
        load_instance = True
        sqla_session = db.session
