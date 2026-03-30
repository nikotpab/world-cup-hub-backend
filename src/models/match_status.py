from src.database import db
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema

class MatchStatus(db.Model):
    __tablename__ = "MATCH_STATUS"
    
    matchStatusId = db.Column('id_match_status', db.Integer, primary_key=True, autoincrement=True)
    nameStatus = db.Column('name_status', db.String(4000), nullable=False)
    matchId = db.Column('MATCH_match_id', db.Integer, db.ForeignKey('MATCH.match_id'), nullable=False)
    match = db.relationship('Match', backref='match_statuses')
    
    def create(self):
        db.session.add(self)
        db.session.commit()
        return self

class MatchStatusSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = MatchStatus
        load_instance = True
        sqla_session = db.session
