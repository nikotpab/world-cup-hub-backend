from src.database import db
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema 
from marshmallow import fields

class User(db.Model):
    __tablename__ = "USER"
    
    userId = db.Column(db.Integer, primary_key=True, autoincrement=True)
    identification = db.Column(db.Integer, nullable=False)
    password = db.Column(db.String(20), nullable=False)
    firstName = db.Column(db.String(20), nullable=False)
    lastName = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(30), nullable=False)
    registeredAt = db.Column(db.DateTime, nullable=False)
    
    def create(self):
        db.session.add(self)
        db.session.commit()
        return self

class UserSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = User
        load_instance = True  
        sqla_session = db.session
