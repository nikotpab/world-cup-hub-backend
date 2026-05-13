from app.infrastructure.database import db
from app.domain.models.role import Role

class User(db.Model):
    __tablename__ = "usuario"
    
    userId = db.Column('id_usuario', db.Integer, primary_key=True, autoincrement=True)
    firstName = db.Column('nombre', db.String(100), nullable=False)
    lastName = db.Column('apellido', db.String(100), nullable=False)
    email = db.Column('correo_electronico', db.String(150), unique=True, nullable=False)
    password = db.Column('contrasena', db.String(255), nullable=False)
    roleId = db.Column('id_rol', db.Integer, db.ForeignKey('rol.id_rol'), nullable=True)
    registeredAt = db.Column('fecha_registro', db.DateTime, nullable=True, default=db.func.current_timestamp())
    lastAccess = db.Column('ultimo_acceso', db.DateTime, nullable=True)
    accountStatus = db.Column('estado_cuenta', db.String(20), default='activo')
    verified = db.Column('verificado', db.Boolean, default=False)
    verificationCode = db.Column('codigo_verificacion', db.String(6), nullable=True)
    
    role = db.relationship('Role', backref='users')

