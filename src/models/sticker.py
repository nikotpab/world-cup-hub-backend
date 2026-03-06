from src.database import db
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema 
from marshmallow import fields

class Sticker(db.Model):
    __tablename__ = "STICKER"
    
    stickerId = db.Column(db.Integer, primary_key=True, autoincrement=True)
    category = db.Column(db.String(20), nullable=False)
    name = db.Column(db.String(50), nullable=False)
    rarity = db.Column(db.String(1), nullable=False)
    team = db.Column(db.String(20), nullable=False)
    
    def create(self):
        db.session.add(self)
        db.session.commit()
        return self

class StickerSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Sticker
        load_instance = True  
        sqla_session = db.session
