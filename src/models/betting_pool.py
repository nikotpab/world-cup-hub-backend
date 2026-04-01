from src.database import db
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema 
from marshmallow import fields

user_bett = db.Table('USER_BETT',
    db.Column('USER_user_id', db.Integer, db.ForeignKey('USER.user_id'), primary_key=True),
    db.Column('BETTING_POOL_betting_team_id', db.Integer, db.ForeignKey('BETTING_POOL.betting_team_id'), primary_key=True),
    db.Column('is_admin', db.String(1), nullable=False),
    extend_existing=True
)

class BettingPool(db.Model):
    __tablename__ = "BETTING_POOL"
    
    bettingPoolId = db.Column('betting_team_id', db.Integer, primary_key=True, autoincrement=True)
    name = db.Column('name', db.String(200), nullable=False)
    invitationCode = db.Column('invitation_code', db.Integer, nullable=False)
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
