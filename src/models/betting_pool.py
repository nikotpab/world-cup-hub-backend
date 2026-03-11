from src.database import db
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema 
from marshmallow import fields

user_bett = db.Table('USER_BETT',
    db.Column('USER_user_id', db.Integer, db.ForeignKey('USER.userId'), primary_key=True),
    db.Column('BETTING_TEAM_betting_team_id', db.Integer, db.ForeignKey('BETTING_POOL.bettingPoolId'), primary_key=True),
    db.Column('is_admin', db.String(1), nullable=False)
)

class BettingPool(db.Model):
    __tablename__ = "BETTING_POOL"
    
    bettingPoolId = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(30), nullable=False)
    invitationCode = db.Column(db.Integer, nullable=False)
    users = db.relationship('User', secondary='USER_BETT', backref='betting_pools')
    
    def create(self):
        db.session.add(self)
        db.session.commit()
        return self

class BettingPoolSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = BettingPool
        load_instance = True  
        sqla_session = db.session
