from app.infrastructure.database import db

class Prediction(db.Model):
    __tablename__ = "PREDICTION"
    
    predictionId = db.Column('prediction_id', db.Integer, primary_key=True, autoincrement=True)
    homeGoals = db.Column('home_goals', db.Integer, nullable=True)
    awayGoals = db.Column('away_goals', db.Integer, nullable=False)
    bettingPoolId = db.Column('BETTING_POOL_betting_team_id', db.Integer, db.ForeignKey('BETTING_POOL.betting_team_id'), nullable=False)
    matchId = db.Column('MATCH_match_id', db.Integer, db.ForeignKey('MATCH.match_id'), nullable=False)
    userId = db.Column('USER_user_id', db.Integer, db.ForeignKey('USER.user_id'), nullable=False)
    
    # Campo para Optimistic Locking (Prevención de colisiones en la Polla)
    version_id = db.Column(db.Integer, nullable=False, default=1)
    
    betting_pool = db.relationship('BettingPool', backref='predictions')
    match = db.relationship('Match', backref='predictions')
    user = db.relationship('User', backref='predictions')

    __mapper_args__ = {
        'version_id_col': version_id
    }
