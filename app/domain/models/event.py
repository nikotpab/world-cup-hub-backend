from app.infrastructure.database import db

class Event(db.Model):
    __tablename__ = "EVENT"
    
    eventId = db.Column('event_id', db.Integer, primary_key=True, autoincrement=True)
    type = db.Column('type', db.String(100), nullable=False)
    description = db.Column('description', db.String(200), nullable=False)
    auditId = db.Column('AUDIT_audit_id', db.Integer, db.ForeignKey('AUDIT.audit_id'), nullable=False)
    audit = db.relationship('Audit', backref='events')
        db.session.add(self)
        db.session.commit()
        return self
