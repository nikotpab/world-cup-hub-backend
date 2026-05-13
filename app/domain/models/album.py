from app.infrastructure.database import db

sticker_album = db.Table('STICKER_ALBUM',
    db.Column('STICKER_card_id', db.Integer, db.ForeignKey('STICKER.card_id'), primary_key=True),
    db.Column('ALBUM_album_id', db.Integer, db.ForeignKey('ALBUM.album_id'), primary_key=True),
    extend_existing=True
)

class Album(db.Model):
    __tablename__ = "ALBUM"
    
    albumId = db.Column('album_id', db.Integer, primary_key=True, autoincrement=True)
    userId = db.Column('USER_user_id', db.Integer, db.ForeignKey('usuario.id_usuario'), nullable=False)
    user = db.relationship('User', backref='albums')
    stickers = db.relationship('Sticker', secondary='STICKER_ALBUM', backref='albums')

    def save(self):
        db.session.add(self)
        db.session.commit()
        return self
