from src.database import db
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema 
from marshmallow import fields

class Audit(db.Model):
    __tablename__ = "AUDIT"
    
    auditId = db.Column('audit_id', db.Integer, primary_key=True, autoincrement=True)
    correlationId = db.Column('correlation_id', db.Integer, nullable=False)
    result = db.Column('result', db.String(200), nullable=False)
    affectedEntity = db.Column('affected_entity', db.String(200), nullable=False)
    action = db.Column('action', db.String(200), nullable=False)
    timestamp = db.Column('date_hour', db.DateTime, nullable=False)
    userId = db.Column('USER_user_id', db.Integer, db.ForeignKey('USER.user_id'), nullable=False)
    user = db.relationship('User', backref='audits')
    
    def create(self):
        db.session.add(self)
        db.session.commit()
        return self

class AuditSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Audit
        load_instance = True  
        sqla_session = db.session
