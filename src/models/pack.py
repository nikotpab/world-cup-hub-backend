from src.database import db
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema 
from marshmallow import fields

class Pack(db.Model):
    __tablename__ = "PACK"
    
    packId = db.Column(db.Integer, primary_key=True, autoincrement=True)
    openedAt = db.Column(db.DateTime, nullable=False)
    
    def create(self):
        db.session.add(self)
        db.session.commit()
        return self

class PackSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Pack
        load_instance = True  
        sqla_session = db.session
