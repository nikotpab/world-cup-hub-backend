from src.database import db
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema 
from marshmallow import fields

class BettingPool(db.Model):
    __tablename__ = "BETTING_POOL"
    
    bettingPoolId = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(30), nullable=False)
    invitationCode = db.Column(db.Integer, nullable=False)
    
    def create(self):
        db.session.add(self)
        db.session.commit()
        return self

class BettingPoolSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = BettingPool
        load_instance = True  
        sqla_session = db.session
