from src.database import db
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema 
from marshmallow import fields

class Role(db.Model):
    __tablename__ = "ROLE"
    
    roleId = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(30), nullable=False)
    
    def create(self):
        db.session.add(self)
        db.session.commit()
        return self

class RoleSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Role
        load_instance = True  
        sqla_session = db.session
