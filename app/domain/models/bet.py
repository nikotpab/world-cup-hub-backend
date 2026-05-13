from app.infrastructure.database import db

class Bet(db.Model):
    __tablename__ = "BET"
    
    bet_id = db.Column('bet_id', db.Integer, primary_key=True, autoincrement=True)
    home_goals = db.Column('home_goals', db.Integer, nullable=True)
    away_goals = db.Column('away_goals', db.Integer, nullable=False)
    match_id = db.Column('MATCH_match_id', db.Integer, db.ForeignKey('MATCH.match_id'), nullable=False)
    user_id = db.Column('USER_user_id', db.Integer, db.ForeignKey('USER.user_id'), nullable=False)
    
    # Campo para Optimistic Locking (Prevención de colisiones)
    version_id = db.Column(db.Integer, nullable=False, default=1)
    
    match = db.relationship('Match', backref='bets')
    user = db.relationship('User', backref='bets')

    __mapper_args__ = {
        'version_id_col': version_id
    }
