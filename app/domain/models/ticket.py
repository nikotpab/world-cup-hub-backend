from app.infrastructure.database import db

VALID_STATUSES = ('Disponible', 'Reservada', 'Pagada', 'Transferida', 'Reembolsada', 'Expirada')

class Ticket(db.Model):
    __tablename__ = "ticket"

    ticketId       = db.Column('id_ticket',       db.Integer, primary_key=True, autoincrement=True)
    status         = db.Column('status',           db.String(50), nullable=False, default='Disponible')
    price          = db.Column('price',            db.Numeric(10, 2))
    reservedAt     = db.Column('reserved_at',      db.DateTime)
    expirationDate = db.Column('expiration_date',  db.DateTime)
    paidAt         = db.Column('paid_at',          db.DateTime)
    correlationId  = db.Column('correlation_id',   db.String(36))
    matchId        = db.Column('id_match', db.Integer, db.ForeignKey('match.idmatch'))
    userId         = db.Column('id_user',  db.Integer, db.ForeignKey('USER.iduser'))

    match = db.relationship('Match', backref='tickets')
    user  = db.relationship('User',  backref='tickets')

    def save(self):
        db.session.add(self)
        db.session.commit()
        return self
