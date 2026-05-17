import pytest
from datetime import datetime, timedelta, date
from app.application.services.album_service import AlbumService
from app.application.services.trade_service import TradeService
from app.infrastructure.repositories.trade_repository import SqlAlchemyTradeRepository
from app.domain.models.user import User
from app.domain.models.album import Album
from app.domain.models.sticker import Sticker
from app.domain.models.rarity_cat import RarityCat
from app.domain.models.promo_code import PromoCode
from app.infrastructure.database import db

@pytest.fixture
def album_service():
    return AlbumService()

@pytest.fixture
def trade_service():
    repo = SqlAlchemyTradeRepository()
    return TradeService(repository=repo)

@pytest.fixture
def test_user():
    user = User(
        firstName="Test",
        lastName="User",
        email="test@example.com",
        password="password",
        identification=12345678
    )
    db.session.add(user)
    db.session.commit()
    return user

@pytest.fixture
def other_user():
    user = User(
        firstName="Other",
        lastName="User",
        email="other@example.com",
        password="password",
        identification=87654321
    )
    db.session.add(user)
    db.session.commit()
    return user

@pytest.fixture
def setup_stickers():
    # Clean previous data
    db.session.query(Sticker).delete()
    db.session.query(RarityCat).delete()
    db.session.commit()
    
    # Create rarity categories
    common = RarityCat(name="Common")
    rare = RarityCat(name="Rare")
    db.session.add(common)
    db.session.add(rare)
    db.session.commit()
    
    # Create stickers - ensure we have at least 15 unique stickers
    for i in range(10):
        st = Sticker(
            name=f"Player {i}",
            category="Player",
            rarity="Common",
            team="Team A",
            raretyCatId=common.rarityCatId
        )
        db.session.add(st)
    
    for i in range(10): # Incremental unique stickers
        st = Sticker(
            name=f"Star {i}",
            category="Player",
            rarity="Rare",
            team="Team A",
            raretyCatId=rare.rarityCatId
        )
        db.session.add(st)
    db.session.commit()

def test_claim_daily_reward(test_user, album_service):
    # First time claim
    result = album_service.claim_daily_reward(test_user.idUser)
    assert result['success'] is True
    assert result['packs_awarded'] == 1
    
    # Second time same day
    result = album_service.claim_daily_reward(test_user.idUser)
    assert result['success'] is False
    assert "reclamado" in result['message']

def test_redeem_promo_code(test_user, album_service):
    promo = PromoCode(
        code="WORLD_CUP_2026",
        rewardPacks=5,
        rewardCoins=100,
        maxUses=10,
        expiryDate=datetime.now() + timedelta(days=7)
    )
    db.session.add(promo)
    db.session.commit()
    
    result = album_service.redeem_promo_code(test_user.idUser, "WORLD_CUP_2026")
    assert result['success'] is True
    
    album = Album.query.filter_by(idUser=test_user.idUser).first()
    assert album.packBalance == 5
    assert album.coins == 100

def test_open_pack_weighted(test_user, album_service, setup_stickers):
    # Add a pack to user
    album = Album(idUser=test_user.idUser, packBalance=1)
    db.session.add(album)
    db.session.commit()
    
    result = album_service.open_pack(test_user.idUser)
    assert result['success'] is True
    assert len(result['stickers']) == 5
    
    # Refresh album from DB
    db.session.refresh(album)
    assert len(album.stickers) == 5

def test_convert_duplicates(test_user, album_service, setup_stickers):
    album = Album(idUser=test_user.idUser, packBalance=0, coins=0)
    db.session.add(album)
    db.session.commit()
    
    # Give same sticker twice
    st = Sticker.query.first()
    from app.domain.models.album import sticker_album
    ins = sticker_album.insert().values(id_album=album.idAlbum, id_sticker=st.idSticker)
    db.session.execute(ins)
    db.session.execute(ins)
    db.session.commit()
    
    result = album_service.convert_duplicates_to_coins(test_user.idUser)
    assert result['success'] is True
    
    db.session.refresh(album)
    # One sticker remains, one converted
    assert len(album.stickers) == 1
    assert album.coins > 0

def test_confirm_trade_with_transfer(test_user, other_user, trade_service, setup_stickers):
    album_test = Album(idUser=test_user.idUser).save()
    album_other = Album(idUser=other_user.idUser).save()
    
    s1 = Sticker.query.all()[0]
    s2 = Sticker.query.all()[1]
    
    from app.domain.models.album import sticker_album
    db.session.execute(sticker_album.insert().values(id_album=album_test.idAlbum, id_sticker=s1.idSticker))
    db.session.execute(sticker_album.insert().values(id_album=album_other.idAlbum, id_sticker=s2.idSticker))
    db.session.commit()
    
    # Test user offers s1 for other_user's s2
    data = {
        "proposer_id": test_user.idUser,
        "receiver_id": other_user.idUser,
        "offered_sticker_id": s1.idSticker,
        "requested_sticker_id": s2.idSticker
    }
    proposal = trade_service.propose_trade(data)
    
    # Confirm trade
    result = trade_service.confirm_trade(proposal.id)
    assert result.status == 'COMPLETED'
    
    # Refresh albums
    db.session.refresh(album_test)
    db.session.refresh(album_other)
    
    # Verify stickers swapped
    assert any(s.idSticker == s2.idSticker for s in album_test.stickers)
    assert any(s.idSticker == s1.idSticker for s in album_other.stickers)

def test_trade_limit(test_user, other_user, trade_service, setup_stickers):
    album_test = Album(idUser=test_user.idUser).save()
    album_other = Album(idUser=other_user.idUser).save()
    
    s1 = Sticker.query.all()[0]
    s2 = Sticker.query.all()[1]
    
    from app.domain.models.album import sticker_album
    
    # Mock 5 successful trades today
    for _ in range(5):
        # Reset stickers for each iteration
        db.session.execute(sticker_album.delete().where(sticker_album.c.id_album.in_([album_test.idAlbum, album_other.idAlbum])))
        db.session.execute(sticker_album.insert().values(id_album=album_test.idAlbum, id_sticker=s1.idSticker))
        db.session.execute(sticker_album.insert().values(id_album=album_other.idAlbum, id_sticker=s2.idSticker))
        db.session.commit()
        
        data = {
            "proposer_id": test_user.idUser,
            "receiver_id": other_user.idUser,
            "offered_sticker_id": s1.idSticker,
            "requested_sticker_id": s2.idSticker
        }
        prop = trade_service.propose_trade(data)
        trade_service.confirm_trade(prop.id)
        
    # 6th trade proposal should fail
    data = {
        "proposer_id": test_user.idUser,
        "receiver_id": other_user.idUser,
        "offered_sticker_id": s1.idSticker,
        "requested_sticker_id": s2.idSticker
    }
    
    with pytest.raises(ValueError) as excinfo:
        trade_service.propose_trade(data)
    
    assert "límite diario" in str(excinfo.value)
