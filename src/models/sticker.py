from src.database import db
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema 
from marshmallow import fields

class Sticker(db.Model):
    __tablename__ = "STICKER"
    
    stickerId = db.Column('card_id', db.Integer, primary_key=True, autoincrement=True)
    category = db.Column('category', db.String(200), nullable=False)
    name = db.Column('name', db.String(200), nullable=False)
    rarity = db.Column('rarity', db.String(200), nullable=False)
    team = db.Column('team', db.String(200), nullable=False)
    raretyCatId = db.Column('RARYTY_CAT_rarety_cat_id', db.Integer, db.ForeignKey('RARYTY_CAT.rarety_cat_id'), nullable=False)
    rarityCat = db.relationship('RarityCat', backref='stickers')
    
    def create(self):
        db.session.add(self)
        db.session.commit()
        return self

class StickerSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Sticker
        load_instance = True  
        sqla_session = db.session
