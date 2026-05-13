from app.infrastructure.database import db

class TicketHistory(db.Model):
    __tablename__ = "TICKET_HISTORY"
    
    historyId = db.Column('id_ticked_history', db.Integer, primary_key=True, autoincrement=True)
    status = db.Column('status', db.String(50), nullable=False)
    reason = db.Column('reason', db.String(4000), nullable=False)
    changedAt = db.Column('changedAt', db.DateTime, nullable=False)
    ticketId = db.Column('TICKET_ticket_id', db.Integer, nullable=False)
    userId = db.Column('TICKET_USER_user_id', db.Integer, nullable=False)
    
    __table_args__ = (
        db.ForeignKeyConstraint(
            ['TICKET_ticket_id', 'TICKET_USER_user_id'],
            ['TICKET.ticket_id', 'TICKET.USER_user_id']
        ),
    )
    
    ticket = db.relationship('Ticket', backref='history')

    def save(self):
        db.session.add(self)
        db.session.commit()
        return self
