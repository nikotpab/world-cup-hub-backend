from app.infrastructure.database import db

class Role(db.Model):
    __tablename__ = "role"
    
    idRole = db.Column('idrole', db.Integer, primary_key=True, autoincrement=True)
    roleName = db.Column('rolename', db.String(50), nullable=False)

    def save(self):
        db.session.add(self)
        db.session.commit()
        return self
