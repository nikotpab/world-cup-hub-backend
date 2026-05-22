from datetime import datetime, timezone
from app.infrastructure.database import db

class SportsBet(db.Model):
    __tablename__ = "sports_bet"

    id             = db.Column('id',            db.Integer,     primary_key=True, autoincrement=True)
    userId         = db.Column('user_id',        db.Integer,     db.ForeignKey('USER.iduser'), nullable=False)
    matchId        = db.Column('match_id',       db.Integer,     nullable=False)
    homeName       = db.Column('home_name',      db.String(100), nullable=False)
    awayName       = db.Column('away_name',      db.String(100), nullable=False)
    betType        = db.Column('bet_type',       db.String(30),  nullable=False)
    # 'home_win' | 'draw' | 'away_win' | 'score_H-A'
    betLabel       = db.Column('bet_label',      db.String(100), nullable=False)
    odds           = db.Column('odds',           db.Float,       nullable=False)
    stake          = db.Column('stake',          db.Integer,     nullable=False)   # en monedas
    potentialWin   = db.Column('potential_win',  db.Integer,     nullable=False)
    status         = db.Column('status',         db.String(20),  nullable=False, default='pending')
    # 'pending' | 'won' | 'lost' | 'cancelled'
    createdAt      = db.Column('created_at',     db.DateTime,    default=lambda: datetime.now(timezone.utc).replace(tzinfo=None))
    settledAt      = db.Column('settled_at',     db.DateTime,    nullable=True)
    stripeIntentId = db.Column('stripe_intent_id', db.String(255),  nullable=True)

    user = db.relationship('User', backref='sports_bets')
