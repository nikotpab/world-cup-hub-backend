import os
os.environ.setdefault("FLASK_ENV", "production")
from app import create_app
from app.infrastructure.database import db
from app.domain.models.sticker import Sticker
from app.domain.models.album import sticker_album
from app.domain.models.pack import pack_sticker
from app.domain.models.trade_proposal import TradeProposal

app = create_app()
with app.app_context():
    print("Deleting all trade proposals...")
    TradeProposal.query.delete()
    print("Deleting all associations from album_sticker...")
    db.session.execute(sticker_album.delete())
    print("Deleting all associations from pack_sticker...")
    db.session.execute(pack_sticker.delete())
    print("Deleting all stickers...")
    Sticker.query.delete()
    db.session.commit()
    print("Database is now clean!")
