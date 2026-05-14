from app.infrastructure.database import db

class Sticker(db.Model):
    __tablename__ = "sticker"

    idSticker   = db.Column('id_sticker',    db.Integer, primary_key=True, autoincrement=True)
    name        = db.Column('name',          db.String(100), nullable=False)
    category    = db.Column('category',      db.String(50),  nullable=False)
    rarity      = db.Column('rarity',        db.String(50),  nullable=False)
    team        = db.Column('team',          db.String(100), nullable=False)
    paniniCode  = db.Column('panini_code',   db.String(50),  nullable=True)
    position    = db.Column('position',      db.String(50),  nullable=True)
    nationality = db.Column('nationality',   db.String(100), nullable=True)
    raretyCatId = db.Column('rarety_cat_id', db.Integer, db.ForeignKey('raryty_cat.rarety_cat_id'), nullable=False)

    rarityCat = db.relationship('RarityCat', backref='stickers')
