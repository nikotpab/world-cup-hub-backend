from app.infrastructure.database import db

class Match(db.Model):
    __tablename__ = "MATCH"
    
    matchId = db.Column('match_id', db.Integer, primary_key=True, autoincrement=True)
    status = db.Column('status', db.String(50), nullable=False)
    phase = db.Column('phase', db.String(50), nullable=False)
    scheduledAt = db.Column('date_hour', db.DateTime, nullable=False)
    stadiumId = db.Column('STADIUM_stadium_id', db.Integer, db.ForeignKey('STADIUM.stadium_id'), nullable=False)
    
    homeTeamId = db.Column('home_team_id', db.Integer, db.ForeignKey('NATIONAL_TEAM.national_team_id'), nullable=True)
    awayTeamId = db.Column('away_team_id', db.Integer, db.ForeignKey('NATIONAL_TEAM.national_team_id'), nullable=True)
    
    homeGoals = db.Column('home_goals', db.Integer, nullable=True)
    awayGoals = db.Column('away_goals', db.Integer, nullable=True)

    stadium = db.relationship('Stadium', backref='matches')
    homeTeam = db.relationship('NationalTeam', foreign_keys=[homeTeamId], backref='home_matches')
    awayTeam = db.relationship('NationalTeam', foreign_keys=[awayTeamId], backref='away_matches')
