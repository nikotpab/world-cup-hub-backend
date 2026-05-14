from app.infrastructure.database import db

class Transfer(db.Model):
    __tablename__ = "transfer"

    idTransfer    = db.Column('id_transfer',    db.Integer, primary_key=True, autoincrement=True)
    transferDate  = db.Column('transfer_date',  db.DateTime, default=db.func.current_timestamp())
    correlationId = db.Column('correlation_id', db.String(36))
    fromUserId    = db.Column('from_user_id',   db.Integer, db.ForeignKey('USER.iduser'))
    toUserId      = db.Column('to_user_id',     db.Integer, db.ForeignKey('USER.iduser'))
    ticketId      = db.Column('ticket_id',      db.Integer, db.ForeignKey('ticket.id_ticket'))
    idPayment     = db.Column('id_payment',     db.Integer, db.ForeignKey('payment.id_payment'))

    from_user = db.relationship('User', foreign_keys=[fromUserId], backref='transfers_sent')
    to_user   = db.relationship('User', foreign_keys=[toUserId],   backref='transfers_received')
    ticket    = db.relationship('Ticket', backref='transfers')
    payment   = db.relationship('Payment', backref='transfers')
