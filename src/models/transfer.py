from src.database import db
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema 
from marshmallow import fields

class Transfer(db.Model):
    __tablename__ = "TRANSFER"
    
    transferId = db.Column(db.Integer, primary_key=True, autoincrement=True)
    date = db.Column(db.DateTime, nullable=False)
    
    def create(self):
        db.session.add(self)
        db.session.commit()
        return self

class TransferSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Transfer
        load_instance = True  
        sqla_session = db.session
