from app.infrastructure.database import db

class Audit(db.Model):
    __tablename__ = "audit_log"
    
    idAudit = db.Column('id_audit', db.Integer, primary_key=True, autoincrement=True)
    correlationId = db.Column('correlation_id', db.String(100))
    createdAt = db.Column('created_at', db.DateTime, default=db.func.current_timestamp())
    payload = db.Column('payload', db.Text)
    affectedEntity = db.Column('affected_entity', db.String(100))
    action = db.Column('action', db.String(50))
    result = db.Column('result', db.String(50))

    def save(self):
        db.session.add(self)
        db.session.commit()
        return self
