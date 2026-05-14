from app.infrastructure.database import db

class NationalTeam(db.Model):
    __tablename__ = "national_team"
    
    idNationalTeam = db.Column('national_team_id', db.Integer, primary_key=True, autoincrement=True)
    name = db.Column('name', db.String(100), nullable=True)
    flagUrl = db.Column('flag_url', db.String(255))
    idTeam = db.Column('id_team', db.Integer, db.ForeignKey('team.idteam'))
    
    team = db.relationship('Team', backref='national_teams')

# Helper table to align with SQL script naming
sta_nat = db.Table('sta_nat',
    db.Column('national_team_id', db.Integer, db.ForeignKey('national_team.national_team_id'), primary_key=True),
    db.Column('stadium_id', db.Integer, db.ForeignKey('stadium.idstadium'), primary_key=True)
)
