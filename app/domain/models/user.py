from app.infrastructure.database import db
from app.domain.models.role import Role

class User(db.Model):
    __tablename__ = "USER"
    
    idUser = db.Column('iduser', db.Integer, primary_key=True, autoincrement=True)
    firstName = db.Column('firstname', db.String(100), nullable=False)
    lastName = db.Column('lastname', db.String(100), nullable=False)
    identification = db.Column('identification', db.Integer, nullable=False)
    email = db.Column('email', db.String(100), unique=True, nullable=False)
    password = db.Column('password', db.String(255), nullable=False)
    createdAt = db.Column('createdat', db.DateTime, default=db.func.current_timestamp())
    idRole = db.Column('idrole', db.Integer, db.ForeignKey('role.idrole'), default=2)
    verified = db.Column('verified', db.Boolean, default=False)
    verificationCode = db.Column('verificationcode', db.String(6), nullable=True)
    accountStatus = db.Column('accountstatus', db.String(20), default='activo')
    
    role = db.relationship('Role', backref='users')
