from app.infrastructure.database import db

class TicketHistory(db.Model):
    __tablename__ = "ticket_history"
    
    idHistory = db.Column('id_history', db.Integer, primary_key=True, autoincrement=True)
    status = db.Column('status', db.String(50))
    changedAt = db.Column('changed_at', db.DateTime, default=db.func.current_timestamp())
    reason = db.Column('reason', db.Text)
    idTicket = db.Column('id_ticket', db.Integer, db.ForeignKey('ticket.id_ticket'))
    
    ticket = db.relationship('Ticket', backref='history')
