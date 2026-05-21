from app.infrastructure.database import db

class Bet(db.Model):
    __tablename__ = "prediction"
    
    bet_id = db.Column('id_prediction', db.Integer, primary_key=True, autoincrement=True)
    home_goals = db.Column('home_goals', db.Integer, nullable=False)
    away_goals = db.Column('away_goals', db.Integer, nullable=False)
    match_id = db.Column('id_match', db.Integer, db.ForeignKey('match.idmatch'), nullable=False)
    user_id = db.Column('id_user', db.Integer, db.ForeignKey('USER.iduser'), nullable=False)
    createdAt = db.Column('created_at', db.DateTime, default=db.func.current_timestamp())
    
    # Campo para Optimistic Locking (Prevención de colisiones)
    version_id = db.Column('version_id', db.Integer, nullable=False, default=1)
    
    match = db.relationship('Match', backref='bets')
    user = db.relationship('User', backref='bets')

    __mapper_args__ = {
        'version_id_col': version_id
    }
