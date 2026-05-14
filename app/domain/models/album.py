from app.infrastructure.database import db

sticker_album = db.Table('album_sticker',
    db.Column('id', db.Integer, primary_key=True, autoincrement=True),
    db.Column('id_sticker', db.Integer, db.ForeignKey('sticker.id_sticker')),
    db.Column('id_album', db.Integer, db.ForeignKey('album.id_album')),
    extend_existing=True
)

class Album(db.Model):
    __tablename__ = "album"
    
    idAlbum = db.Column('id_album', db.Integer, primary_key=True, autoincrement=True)
    idUser = db.Column('id_user', db.Integer, db.ForeignKey('USER.iduser'), unique=True, nullable=False)
    packBalance = db.Column('pack_balance', db.Integer, default=0)
    coins = db.Column('coins', db.Integer, default=0)
    lastRewardDate = db.Column('last_reward_date', db.Date, nullable=True)
    
    user = db.relationship('User', backref='albums')
    stickers = db.relationship('Sticker', secondary=sticker_album, backref='albums')

    def save(self):
        db.session.add(self)
        db.session.commit()
        return self
