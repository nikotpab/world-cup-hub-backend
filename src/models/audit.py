from src.database import db
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema 
from marshmallow import fields

class Audit(db.Model):
    __tablename__ = "AUDIT"
    
    auditId = db.Column(db.Integer, primary_key=True, autoincrement=True)
    correlationId = db.Column(db.Integer, nullable=False)
    result = db.Column(db.String(200), nullable=False)
    payload = db.Column(db.String(200), nullable=False)
    affectedEntity = db.Column(db.String(30), nullable=False)
    action = db.Column(db.String(200), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False)
    
    def create(self):
        db.session.add(self)
        db.session.commit()
        return self

class AuditSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Audit
        load_instance = True  
        sqla_session = db.session
