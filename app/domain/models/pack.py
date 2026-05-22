from app.infrastructure.database import db

pack_sticker = db.Table('pack_sticker',
    db.Column('id', db.Integer, primary_key=True, autoincrement=True),
    db.Column('id_sticker', db.Integer, db.ForeignKey('sticker.id_sticker')),
    db.Column('id_pack', db.Integer, db.ForeignKey('pack.id_pack')),
    extend_existing=True
)

class Pack(db.Model):
    __tablename__ = "pack"
    
    idPack = db.Column('id_pack', db.Integer, primary_key=True, autoincrement=True)
    openedAt = db.Column('opened_at', db.DateTime, default=db.func.current_timestamp())
    idUser = db.Column('id_user', db.Integer, db.ForeignKey('USER.iduser'), nullable=False)
    
    user = db.relationship('User', backref='packs')
    stickers = db.relationship('Sticker', secondary=pack_sticker, backref='packs')

    def save(self):
        db.session.add(self)
        db.session.commit()
        return self
