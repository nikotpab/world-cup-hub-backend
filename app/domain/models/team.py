from app.infrastructure.database import db

class Team(db.Model):
    __tablename__ = "TEAM"
    
    teamId = db.Column('id_team', db.Integer, primary_key=True, autoincrement=True)
    name = db.Column('name', db.String(4000), nullable=False)
        db.session.add(self)
        db.session.commit()
        return self
