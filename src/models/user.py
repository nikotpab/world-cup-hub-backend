from src.database import db
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema 
from marshmallow import fields

class User(db.Model):
    __tablename__ = "USER"
    
    userId = db.Column('user_id', db.Integer, primary_key=True, autoincrement=True)
    identification = db.Column('identification', db.Integer, nullable=False)
    password = db.Column('password', db.String(200), nullable=True)
    firstName = db.Column('name', db.String(200), nullable=False)
    lastName = db.Column('last_name', db.String(200), nullable=False)
    email = db.Column('email', db.String(200), nullable=False)
    registeredAt = db.Column('registration_date', db.DateTime, nullable=True)
    roleId = db.Column('ROLE_role_id', db.Integer, db.ForeignKey('ROLE.role_id'), nullable=False)
    role = db.relationship('Role', backref='users')
    
    def create(self):
        db.session.add(self)
        db.session.commit()
        return self

class UserSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = User
        load_instance = True  
        sqla_session = db.session
