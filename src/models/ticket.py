from src.database import db
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema 
from marshmallow import fields

class Ticket(db.Model):
    __tablename__ = "TICKET"
    
    ticketId = db.Column(db.Integer, primary_key=True, autoincrement=True)
    status = db.Column(db.String(1), nullable=False)
    reservationDate = db.Column(db.DateTime, nullable=False)
    expirationDate = db.Column(db.DateTime, nullable=False)
    price = db.Column(db.Float, nullable=False)
    matchId = db.Column(db.Integer, db.ForeignKey('MATCH.matchId'), nullable=False)
    userId = db.Column(db.Integer, db.ForeignKey('USER.userId'), nullable=False)
    match = db.relationship('Match', backref='tickets')
    user = db.relationship('User', backref='tickets')
    
    def create(self):
        db.session.add(self)
        db.session.commit()
        return self

class TicketSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Ticket
        load_instance = True  
        sqla_session = db.session
