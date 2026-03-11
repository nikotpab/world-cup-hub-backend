from src.database import db
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema 
from marshmallow import fields

card_album = db.Table('CARD_ALBUM',
    db.Column('CARD_card_id', db.Integer, db.ForeignKey('STICKER.stickerId'), primary_key=True),
    db.Column('ALBUM_album_id', db.Integer, db.ForeignKey('ALBUM.albumId'), primary_key=True)
)

class Album(db.Model):
    __tablename__ = "ALBUM"
    
    albumId = db.Column(db.Integer, primary_key=True, autoincrement=True)
    userId = db.Column(db.Integer, db.ForeignKey('USER.userId'), nullable=False)
    user = db.relationship('User', backref='albums')
    stickers = db.relationship('Sticker', secondary='CARD_ALBUM', backref='albums')
    
    def create(self):
        db.session.add(self)
        db.session.commit()
        return self

class AlbumSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Album
        load_instance = True  
        sqla_session = db.session
