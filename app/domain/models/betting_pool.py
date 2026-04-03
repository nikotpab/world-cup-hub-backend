from app.infrastructure.database import db

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
        db.session.add(self)
        db.session.commit()
        return self
