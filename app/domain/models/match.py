from app.infrastructure.database import db

class Match(db.Model):
    __tablename__ = "match"
    
    matchId = db.Column('idmatch', db.Integer, primary_key=True, autoincrement=True)
    scheduledAt = db.Column('matchdate', db.DateTime, nullable=False)
    stadiumId = db.Column('idstadium', db.Integer, db.ForeignKey('stadium.idstadium'), nullable=True)
    home_team_id = db.Column('home_team_id', db.Integer, db.ForeignKey('team.idteam'), nullable=True)
    away_team_id = db.Column('away_team_id', db.Integer, db.ForeignKey('team.idteam'), nullable=True)
    home_team_name = db.Column('home_team_name', db.String(100), nullable=True)
    away_team_name = db.Column('away_team_name', db.String(100), nullable=True)
    ticket_price   = db.Column('ticket_price',   db.Float,       default=150.0)
    home_goals = db.Column('home_goals', db.Integer, default=0)
    away_goals = db.Column('away_goals', db.Integer, default=0)
    status = db.Column('status', db.String(50), default='SCHEDULED')
    
    stadium = db.relationship('Stadium', backref='matches')
    home_team = db.relationship('Team', foreign_keys=[home_team_id], backref='home_matches')
    away_team = db.relationship('Team', foreign_keys=[away_team_id], backref='away_matches')
