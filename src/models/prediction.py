from src.database import db
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema 
from marshmallow import fields

class Prediction(db.Model):
    __tablename__ = "PREDICTION"
    
    predictionId = db.Column('prediction_id', db.Integer, primary_key=True, autoincrement=True)
    homeGoals = db.Column('home_goals', db.Integer, nullable=True)
    awayGoals = db.Column('away_goals', db.Integer, nullable=False)
    bettingPoolId = db.Column('BETTING_POOL_betting_team_id', db.Integer, db.ForeignKey('BETTING_POOL.betting_team_id'), nullable=False)
    matchId = db.Column('MATCH_match_id', db.Integer, db.ForeignKey('MATCH.match_id'), nullable=False)
    userId = db.Column('USER_user_id', db.Integer, db.ForeignKey('USER.user_id'), nullable=False)
    betting_pool = db.relationship('BettingPool', backref='predictions')
    match = db.relationship('Match', backref='predictions')
    user = db.relationship('User', backref='predictions')
    
    def create(self):
        db.session.add(self)
        db.session.commit()
        return self

class PredictionSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Prediction
        load_instance = True  
        sqla_session = db.session
