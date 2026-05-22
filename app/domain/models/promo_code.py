from app.infrastructure.database import db
from datetime import datetime

class PromoCode(db.Model):
    __tablename__ = "PROMO_CODE"
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    code = db.Column(db.String(50), unique=True, nullable=False)
    rewardPacks = db.Column('reward_packs', db.Integer, default=0)
    rewardCoins = db.Column('reward_coins', db.Integer, default=0)
    maxUses = db.Column('max_uses', db.Integer, nullable=True)
    currentUses = db.Column('current_uses', db.Integer, default=0)
    expiryDate = db.Column('expiry_date', db.DateTime, nullable=True)
    createdAt = db.Column('created_at', db.DateTime, default=db.func.current_timestamp())

    def save(self):
        db.session.add(self)
        db.session.commit()
        return self

class PromoCodeUsage(db.Model):
    __tablename__ = "PROMO_CODE_USAGE"
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    promoCodeId = db.Column('promo_code_id', db.Integer, db.ForeignKey('PROMO_CODE.id'), nullable=False)
    userId = db.Column('user_id', db.Integer, db.ForeignKey('USER.iduser'), nullable=False)
    usedAt = db.Column('used_at', db.DateTime, default=db.func.current_timestamp())

    promoCode = db.relationship('PromoCode', backref='usages')
    user = db.relationship('User', backref='promo_usages')

    def save(self):
        db.session.add(self)
        db.session.commit()
        return self
