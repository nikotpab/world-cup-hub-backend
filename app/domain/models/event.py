from app.infrastructure.database import db

class Event(db.Model):
    __tablename__ = "event"
    
    idEvent = db.Column('event_id', db.Integer, primary_key=True, autoincrement=True)
    type = db.Column('type', db.String(50))
    description = db.Column('description', db.Text)
    idAudit = db.Column('audit_id', db.Integer, db.ForeignKey('audit_log.id_audit'))
    
    audit = db.relationship('Audit', backref='events')
