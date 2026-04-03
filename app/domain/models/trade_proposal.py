from app.infrastructure.database import db
from datetime import datetime

class TradeProposal(db.Model):
    __tablename__ = "TRADE_PROPOSAL"
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    proposer_id = db.Column(db.Integer, db.ForeignKey('USER.user_id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('USER.user_id'), nullable=False)
    offered_sticker_id = db.Column(db.Integer, db.ForeignKey('STICKER.card_id'), nullable=False)
    requested_sticker_id = db.Column(db.Integer, db.ForeignKey('STICKER.card_id'), nullable=False)
    
    status = db.Column(db.String(50), nullable=False, default='PENDING_CONFIRMATION')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    proposer = db.relationship('User', foreign_keys=[proposer_id])
    receiver = db.relationship('User', foreign_keys=[receiver_id])
    offered_sticker = db.relationship('Sticker', foreign_keys=[offered_sticker_id])
    requested_sticker = db.relationship('Sticker', foreign_keys=[requested_sticker_id])
