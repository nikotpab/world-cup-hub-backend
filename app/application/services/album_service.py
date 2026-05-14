from typing import Dict, Any, List
import random
from datetime import datetime, date
from app.infrastructure.database import db
from app.domain.models.album import Album, sticker_album
from app.domain.models.pack import Pack, pack_sticker
from app.domain.models.sticker import Sticker
from app.domain.models.promo_code import PromoCode, PromoCodeUsage

class AlbumService:
    def __init__(self):
        pass

    def get_user_album(self, user_id: int) -> Dict[str, Any]:
        album = Album.query.filter_by(idUser=user_id).first()
        if not album:
            album = Album(idUser=user_id)
            db.session.add(album)
            db.session.commit()
            
        all_stickers = album.stickers
            
        unique_stickers = set([s.idSticker for s in all_stickers])
        repeated_stickers_count = len(all_stickers) - len(unique_stickers)
        
        total_available = Sticker.query.count() or 600
        
        collections_map = {}
        for s in all_stickers:
            team_name = s.team
            if team_name not in collections_map:
                collections_map[team_name] = set()
            collections_map[team_name].add(s.idSticker)
            
        collections_list = []
        i = 1
        for team, unique_s in collections_map.items():
            collections_list.append({
                "id": i,
                "name": team,
                "count": len(unique_s)
            })
            i += 1
            
        if not collections_list:
            collections_list = [
                {"id": 1, "name": "Selección Argentina"},
                {"id": 2, "name": "Selección Brasil"},
                {"id": 3, "name": "Selección Francia"}
            ]

        completion_percentage = 0
        if total_available > 0:
            completion_percentage = int((len(unique_stickers) / total_available) * 100)

        return {
            "completion_percentage": completion_percentage,
            "total_stickers": len(unique_stickers),
            "max_stickers": total_available,
            "repeated_stickers": repeated_stickers_count,
            "pack_balance": album.packBalance,
            "coins": album.coins,
            "collections": collections_list
        }

    def claim_daily_reward(self, user_id: int) -> Dict[str, Any]:
        album = Album.query.filter_by(idUser=user_id).first()
        if not album:
            album = Album(idUser=user_id, packBalance=0, coins=0)
            db.session.add(album)
            
        if album.packBalance is None: album.packBalance = 0
        if album.coins is None: album.coins = 0
            
        today = date.today()
        if album.lastRewardDate == today:
            return {"success": False, "message": "Ya has reclamado tu recompensa diaria hoy."}
            
        album.lastRewardDate = today
        album.packBalance += 1
        db.session.commit()
        
        return {
            "success": True,
            "message": "¡Has reclamado 1 sobre de láminas!",
            "pack_balance": album.packBalance,
            "packs_awarded": 1
        }

    def redeem_promo_code(self, user_id: int, code: str) -> Dict[str, Any]:
        promo = PromoCode.query.filter_by(code=code).first()
        if not promo:
            raise ValueError("Código promocional inválido.")
            
        if promo.expiryDate and promo.expiryDate < datetime.utcnow():
            raise ValueError("El código promocional ha expirado.")
            
        if promo.maxUses is not None and promo.currentUses >= promo.maxUses:
            raise ValueError("El código promocional ha alcanzado su límite de usos.")
            
        usage = PromoCodeUsage.query.filter_by(promoCodeId=promo.id, userId=user_id).first()
        if usage:
            raise ValueError("Ya has utilizado este código promocional.")
            
        album = Album.query.filter_by(idUser=user_id).first()
        if not album:
            album = Album(idUser=user_id, packBalance=0, coins=0)
            db.session.add(album)
            
        if album.packBalance is None: album.packBalance = 0
        if album.coins is None: album.coins = 0
            
        album.packBalance += promo.rewardPacks
        album.coins += promo.rewardCoins
        
        promo.currentUses += 1
        usage = PromoCodeUsage(promoCodeId=promo.id, userId=user_id)
        db.session.add(usage)
        
        db.session.commit()
        
        return {
            "success": True,
            "message": f"¡Código canjeado con éxito! Recibiste {promo.rewardPacks} sobres y {promo.rewardCoins} monedas.",
            "pack_balance": album.packBalance,
            "coins": album.coins
        }

    def open_pack(self, user_id: int) -> Dict[str, Any]:
        album = Album.query.filter_by(idUser=user_id).first()
        if not album:
            album = Album(idUser=user_id, packBalance=0, coins=0)
            db.session.add(album)
            
        if album.packBalance is None: album.packBalance = 0
            
        if album.packBalance <= 0:
            raise ValueError("No tienes sobres disponibles para abrir.")
            
        album.packBalance -= 1
        
        rarities = ["Common", "Rare", "Epic", "Legendary"]
        weights = [80, 15, 4, 1]
        
        obtained_stickers = []
        for _ in range(5):
            rarity = random.choices(rarities, weights=weights, k=1)[0]
            stickers_pool = Sticker.query.filter_by(rarity=rarity).all()
            if not stickers_pool:
                stickers_pool = Sticker.query.all()
                
            if stickers_pool:
                obtained_stickers.append(random.choice(stickers_pool))
        
        if not obtained_stickers:
            raise ValueError("No se pudieron generar láminas. Asegúrate de que la base de datos de láminas no esté vacía.")

        new_pack = Pack(
            idUser=user_id,
            openedAt=datetime.utcnow()
        )
        db.session.add(new_pack)
        db.session.flush()

        for st in obtained_stickers:
            # Uso de insert explícito para permitir duplicados en PostgreSQL
            ins_pack = pack_sticker.insert().values(id_pack=new_pack.idPack, id_sticker=st.idSticker)
            db.session.execute(ins_pack)
            ins_album = sticker_album.insert().values(id_album=album.idAlbum, id_sticker=st.idSticker)
            db.session.execute(ins_album)
            
        db.session.commit()
        # Expulsar de la sesión para forzar recarga total de relaciones M2M
        db.session.expire(album)
        
        return {
            "success": True,
            "message": "¡Has abierto un sobre con éxito!",
            "stickers": [{"id": s.idSticker, "name": s.name, "team": s.team, "rarity": s.rarity} for s in obtained_stickers],
            "pack_balance": album.packBalance
        }

    def convert_duplicates_to_coins(self, user_id: int) -> Dict[str, Any]:
        album = Album.query.filter_by(idUser=user_id).first()
        if not album:
            raise ValueError("Álbum no encontrado.")
            
        if album.coins is None: album.coins = 0
            
        # Refrescar e inspeccionar la tabla de unión directamente
        all_associations = db.session.query(sticker_album).filter_by(id_album=album.idAlbum).all()
        
        counts = {}
        for assoc in all_associations:
            counts[assoc.id_sticker] = counts.get(assoc.id_sticker, 0) + 1
            
        rarity_values = {"Common": 10, "Rare": 50, "Epic": 200, "Legendary": 1000}
        total_coins = 0
        to_delete_assoc_ids = []
        
        for sid, count in counts.items():
            if count > 1:
                sticker = db.session.get(Sticker, sid)
                total_coins += rarity_values.get(sticker.rarity, 10) * (count - 1)
                sid_assocs = [a.id for a in all_associations if a.id_sticker == sid]
                to_delete_assoc_ids.extend(sid_assocs[1:])

        if not to_delete_assoc_ids:
            return {"success": False, "message": "No tienes láminas repetidas para convertir."}

        db.session.execute(
            sticker_album.delete().where(sticker_album.c.id.in_(to_delete_assoc_ids))
        )
            
        album.coins += total_coins
        db.session.commit()
        db.session.expire(album)
        
        return {
            "success": True,
            "message": f"¡Has convertido tus repetidas en {total_coins} monedas!",
            "coins": album.coins
        }

    def buy_pack_with_coins(self, user_id: int) -> Dict[str, Any]:
        album = Album.query.filter_by(idUser=user_id).first()
        if not album:
            album = Album(idUser=user_id, packBalance=0, coins=0)
            db.session.add(album)
            
        if album.packBalance is None: album.packBalance = 0
        if album.coins is None: album.coins = 0
            
        pack_cost = 100
        if album.coins < pack_cost:
            raise ValueError(f"No tienes suficientes monedas. El sobre cuesta {pack_cost} monedas.")
            
        album.coins -= pack_cost
        album.packBalance += 1
        db.session.commit()
        
        return {
            "success": True,
            "message": "¡Has comprado un sobre con éxito!",
            "pack_balance": album.packBalance,
            "coins": album.coins
        }
