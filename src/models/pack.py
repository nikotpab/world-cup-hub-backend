from src.database import db
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema 
from marshmallow import fields

package_card = db.Table('PACKAGE_CARD',
    db.Column('CARD_card_id', db.Integer, db.ForeignKey('STICKER.stickerId'), primary_key=True),
    db.Column('PACKAGE_pakage_id', db.Integer, db.ForeignKey('PACK.packId'), primary_key=True)
)

class Pack(db.Model):
    __tablename__ = "PACK"
    
    packId = db.Column(db.Integer, primary_key=True, autoincrement=True)
    openedAt = db.Column(db.DateTime, nullable=False)
    userId = db.Column(db.Integer, db.ForeignKey('USER.userId'), nullable=False)
    user = db.relationship('User', backref='packs')
    stickers = db.relationship('Sticker', secondary='PACKAGE_CARD', backref='packs')
    
    def create(self):
        db.session.add(self)
        db.session.commit()
        return self

class PackSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Pack
        load_instance = True  
        sqla_session = db.session
