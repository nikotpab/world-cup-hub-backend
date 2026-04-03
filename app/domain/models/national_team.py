from app.infrastructure.database import db

sta_nat = db.Table('STA_NAT',
    db.Column('NATIONAL_TEAM_national_team_id', db.Integer, db.ForeignKey('NATIONAL_TEAM.national_team_id'), primary_key=True),
    db.Column('STADIUM_stadium_id', db.Integer, db.ForeignKey('STADIUM.stadium_id'), primary_key=True),
    extend_existing=True
)

class NationalTeam(db.Model):
    __tablename__ = "NATIONAL_TEAM"
    
    nationalTeamId = db.Column('national_team_id', db.Integer, primary_key=True, autoincrement=True)
    name = db.Column('name', db.String(200), nullable=True)
    flagUrl = db.Column('flag_url', db.String(2048), nullable=False)
    teamId = db.Column('TEAM_id_team', db.Integer, db.ForeignKey('TEAM.id_team'), nullable=False)
    stadiums = db.relationship('Stadium', secondary='STA_NAT', backref='national_teams')
    team = db.relationship('Team', backref='national_team')
        db.session.add(self)
        db.session.commit()
        return self
