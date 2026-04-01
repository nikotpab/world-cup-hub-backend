from src.database import db
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema 
from marshmallow import fields

pack_sticker = db.Table('PACK_STICKER',
    db.Column('STICKER_card_id', db.Integer, db.ForeignKey('STICKER.card_id'), primary_key=True),
    db.Column('PACK_pakage_id', db.Integer, db.ForeignKey('PACK.pakage_id'), primary_key=True),
    extend_existing=True
)

class Pack(db.Model):
    __tablename__ = "PACK"
    
    packId = db.Column('pakage_id', db.Integer, primary_key=True, autoincrement=True)
    openedAt = db.Column('aperture_date', db.DateTime, nullable=False)
    userId = db.Column('USER_user_id', db.Integer, db.ForeignKey('USER.user_id'), nullable=False)
    user = db.relationship('User', backref='packs')
    stickers = db.relationship('Sticker', secondary='PACK_STICKER', backref='packs')
    
    def create(self):
        db.session.add(self)
        db.session.commit()
        return self

class PackSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Pack
        load_instance = True  
        sqla_session = db.session
