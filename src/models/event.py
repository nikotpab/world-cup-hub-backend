from src.database import db
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema 
from marshmallow import fields

class Event(db.Model):
    __tablename__ = "EVENT"
    
    eventId = db.Column('event_id', db.Integer, primary_key=True, autoincrement=True)
    type = db.Column('type', db.String(100), nullable=False)
    description = db.Column('description', db.String(200), nullable=False)
    auditId = db.Column('AUDIT_audit_id', db.Integer, db.ForeignKey('AUDIT.audit_id'), nullable=False)
    audit = db.relationship('Audit', backref='events')
    
    def create(self):
        db.session.add(self)
        db.session.commit()
        return self

class EventSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Event
        load_instance = True  
        sqla_session = db.session
