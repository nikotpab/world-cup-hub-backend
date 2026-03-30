from src.database import db
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema

class Team(db.Model):
    __tablename__ = "TEAM"
    
    teamId = db.Column('id_team', db.Integer, primary_key=True, autoincrement=True)
    name = db.Column('name', db.String(4000), nullable=False)
    
    def create(self):
        db.session.add(self)
        db.session.commit()
        return self

class TeamSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Team
        load_instance = True
        sqla_session = db.session
