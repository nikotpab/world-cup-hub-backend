from app.infrastructure.database import db

class Team(db.Model):
    __tablename__ = "team"
    
    idTeam = db.Column('idteam', db.Integer, primary_key=True, autoincrement=True)
    name = db.Column('teamname', db.String(100), nullable=False)
    flagUrl = db.Column('flagurl', db.Text, nullable=False)
