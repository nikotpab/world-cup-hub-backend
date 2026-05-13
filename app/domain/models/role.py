from app.infrastructure.database import db

class Role(db.Model):
    __tablename__ = "rol"
    
    roleId = db.Column('id_rol', db.Integer, primary_key=True, autoincrement=True)
    name = db.Column('nombre_rol', db.String(100), nullable=False)

    def save(self):
        db.session.add(self)
        db.session.commit()
        return self

