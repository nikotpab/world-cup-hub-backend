from app.infrastructure.database import db

class Payment(db.Model):
    __tablename__ = "PAYMENT"
    
    paymentId = db.Column('pay_id', db.Integer, primary_key=True, autoincrement=True)
    status = db.Column('status', db.String(50), nullable=False)
    date = db.Column('date', db.Integer, nullable=False)
    amount = db.Column('amount', db.Float, nullable=False)
    provider = db.Column('supplier', db.String(200), nullable=False)
    ticketId = db.Column('TICKET_ticket_id', db.Integer, db.ForeignKey('TICKET.ticket_id'), nullable=False)
    transferId = db.Column('TRANFER_transfer_id', db.Integer, db.ForeignKey('TRANFER.transfer_id'), nullable=False)
    userId = db.Column('TICKET_USER_user_id', db.Integer, db.ForeignKey('usuario.id_usuario'), nullable=False)
    ticket = db.relationship('Ticket', backref='payments')
    transfer = db.relationship('Transfer', backref='payments')
    user = db.relationship('User', backref='payments')

    def save(self):
        db.session.add(self)
        db.session.commit()
        return self
