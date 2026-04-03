from app.infrastructure.database import db

class Ticket(db.Model):
    __tablename__ = "TICKET"
    
    ticketId = db.Column('ticket_id', db.Integer, primary_key=True)
    status = db.Column('status', db.String(50), nullable=False)
    reservationDate = db.Column('reservation_date', db.DateTime, nullable=True)
    expirationDate = db.Column('expiration_date', db.DateTime, nullable=False)
    price = db.Column('price', db.Float, nullable=False)
    matchId = db.Column('MATCH_match_id', db.Integer, db.ForeignKey('MATCH.match_id'), nullable=False)
    userId = db.Column('USER_user_id', db.Integer, db.ForeignKey('USER.user_id'), primary_key=True, nullable=False)
    match = db.relationship('Match', backref='tickets')
    user = db.relationship('User', backref='tickets')
