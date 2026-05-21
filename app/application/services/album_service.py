from typing import Dict, Any, List
import random
import random as _random_module
from datetime import datetime, date, timezone, timedelta

_rng = _random_module.SystemRandom()
_UTC_MINUS_5 = timezone(timedelta(hours=-5))
from sqlalchemy import func
from app.infrastructure.database import db
from app.domain.models.album import Album, sticker_album
from app.domain.models.pack import Pack, pack_sticker
from app.domain.models.sticker import Sticker
from app.domain.models.promo_code import PromoCode, PromoCodeUsage

class AlbumService:
    DAILY_FREE_PACKS = 3  # packs regalados cada día automáticamente

    def _auto_claim_daily(self, album: "Album") -> None:
        """Reclama los sobres diarios automáticamente si no se han reclamado hoy (UTC-5)."""
        today = datetime.now(_UTC_MINUS_5).date()
        if album.lastRewardDate != today:
            album.lastRewardDate = today
            album.packBalance = (album.packBalance or 0) + self.DAILY_FREE_PACKS
            try:
                from app.infrastructure.external.notification_service import notification_service
                notification_service.notify_user_from_id(
                    user_id=album.idUser,
                    title="🎁 ¡Nuevos sobres disponibles!",
                    body=f"Tienes {self.DAILY_FREE_PACKS} sobres de láminas listos para abrir. ¡Entra a la app!",
                    notif_type="packs",
                )
            except Exception:
                pass

    def get_user_album(self, user_id: int) -> Dict[str, Any]:
        album = Album.query.filter_by(idUser=user_id).first()
        if not album:
            album = Album(idUser=user_id, packBalance=self.DAILY_FREE_PACKS)
            db.session.add(album)
            album.lastRewardDate = date.today()
            db.session.commit()
        else:
            self._auto_claim_daily(album)
            db.session.commit()
            
        all_stickers = album.stickers
            
        unique_stickers = {s.idSticker for s in all_stickers}
        repeated_stickers_count = len(all_stickers) - len(unique_stickers)
        
        total_available = Sticker.query.count() or 600
        
        # Only show teams that have a full "album" set (i.e. have a Team Crest sticker)
        proper_teams = {
            s.team.upper()
            for s in Sticker.query.filter_by(category="Team Crest").all()
        }

        collections_map = {}
        for s in all_stickers:
            # Excluir stickers especiales (no pertenecen a un equipo real)
            if s.category in self._SPECIAL_CATEGORIES or s.team == "WORLD":
                continue
            team_key = s.team.upper()  # normalise: "Argentina" == "ARGENTINA"
            if team_key not in proper_teams:
                continue  # skip API-only teams with incomplete sets
            if team_key not in collections_map:
                collections_map[team_key] = {"display": team_key.title(), "stickers": set()}
            collections_map[team_key]["stickers"].add(s.idSticker)

        flags_map = self._get_flags_mapping()
        collections_list = []
        for i, (team_key, data) in enumerate(collections_map.items(), start=1):
            collections_list.append({
                "id": i,
                "name": data["display"],
                "count": len(data["stickers"]),
                "flagUrl": flags_map.get(team_key),
            })

        if not collections_list:
            collections_list = [
                {"id": 1, "name": "Argentina"},
                {"id": 2, "name": "Colombia"},
                {"id": 3, "name": "Spain"}
            ]

        completion_percentage = 0.0
        if total_available > 0:
            completion_percentage = round((len(unique_stickers) / total_available) * 100, 1)

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
            
        if promo.expiryDate and promo.expiryDate < datetime.now(timezone.utc).replace(tzinfo=None):
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

    DAILY_PACK_LIMIT = 3

    def open_pack(self, user_id: int) -> Dict[str, Any]:
        from datetime import timezone

        album = Album.query.filter_by(idUser=user_id).first()
        if not album:
            album = Album(idUser=user_id, packBalance=0, coins=0)
            db.session.add(album)

        if album.packBalance is None:
            album.packBalance = 0

        # Auto-claim daily packs before checking balance
        self._auto_claim_daily(album)

        if album.packBalance <= 0:
            raise ValueError("No tienes sobres disponibles para abrir.")

        # Progreso antes de abrir para detectar hitos
        owned_before = db.session.query(func.count(sticker_album.c.id_sticker.distinct())).filter(
            sticker_album.c.id_album == album.idAlbum
        ).scalar() or 0

        # Límite diario: 3 sobres por día, usando hora UTC del SERVIDOR
        today_utc_start = datetime.now(timezone.utc).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        packs_today = Pack.query.filter(
            Pack.idUser == user_id,
            Pack.openedAt >= today_utc_start
        ).count()
        if packs_today >= self.DAILY_PACK_LIMIT:
            raise ValueError(
                f"Has alcanzado el límite de {self.DAILY_PACK_LIMIT} sobres por día. "
                "Vuelve mañana (00:00 UTC)."
            )

        album.packBalance -= 1

        def _pick(pool_filter):
            pool = Sticker.query.filter_by(rarity=pool_filter).all()
            if not pool:
                pool = Sticker.query.all()
            return _rng.choice(pool) if pool else None

        obtained_stickers = []
        for slot in range(self._STICKERS_PER_PACK):
            card = _pick(self._pick_rarity_for_slot(slot))
            if card:
                obtained_stickers.append(card)

        if not obtained_stickers:
            raise ValueError("No hay láminas en la base de datos. Ejecuta el seed primero.")

        new_pack = Pack(idUser=user_id, openedAt=datetime.now(timezone.utc))
        db.session.add(new_pack)
        db.session.flush()

        for st in obtained_stickers:
            db.session.execute(pack_sticker.insert().values(id_pack=new_pack.idPack, id_sticker=st.idSticker))
            db.session.execute(sticker_album.insert().values(id_album=album.idAlbum, id_sticker=st.idSticker))

        db.session.commit()
        db.session.expire(album)

        self._notify_album_milestone(user_id, album, owned_before)

        return {
            "success":               True,
            "message":               "¡Has abierto un sobre!",
            "packs_today":           packs_today + 1,
            "packs_remaining_today": self.DAILY_PACK_LIMIT - (packs_today + 1),
            "stickers": [
                {
                    "id": s.idSticker,
                    "name": s.name,
                    "team": s.team,
                    "category": s.category,
                    "rarity": s.rarity,
                    "paniniCode": s.paniniCode,
                }
                for s in obtained_stickers
            ],
            "pack_balance": album.packBalance,
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

    # ------------------------------------------------------------------
    # Progreso del álbum
    # ------------------------------------------------------------------

    # Categorías especiales agrupadas como secciones propias
    _SPECIAL_CATEGORIES = (
        "Golden Baller", "Top Keeper", "Defensive Rock",
        "Midfield Maestro", "Goal Machine", "Master Rookie",
        "Official", "Eternal",
    )
    # Orden de presentación: especiales primero, luego equipos A-Z
    _SPECIAL_ORDER = {k: i for i, k in enumerate(_SPECIAL_CATEGORIES)}

    _STICKERS_PER_PACK = 7
    _FREE       = ["Common", "Rare", "Epic", "Legendary"]
    _W_FREE     = [60, 28, 9, 3]
    _RARE_PLUS  = ["Rare", "Epic", "Legendary"]
    _W_RARE     = [75, 20, 5]
    _EPIC_PLUS  = ["Epic", "Legendary"]
    _W_EPIC     = [80, 20]

    def _pick_rarity_for_slot(self, slot: int) -> str:
        if slot == self._STICKERS_PER_PACK - 1:
            return _rng.choices(self._EPIC_PLUS, weights=self._W_EPIC, k=1)[0]
        if slot == self._STICKERS_PER_PACK - 2:
            return _rng.choices(self._RARE_PLUS, weights=self._W_RARE, k=1)[0]
        return _rng.choices(self._FREE, weights=self._W_FREE, k=1)[0]

    def _notify_album_milestone(self, user_id: int, album, owned_before: int) -> None:
        try:
            total_stickers = Sticker.query.count() or 600
            owned_after = (
                db.session.query(func.count(sticker_album.c.id_sticker.distinct()))
                .filter(sticker_album.c.id_album == album.idAlbum)
                .scalar() or 0
            )
            pct_before = int(owned_before / total_stickers * 100) if total_stickers else 0
            pct_after = int(owned_after / total_stickers * 100) if total_stickers else 0
            for milestone in [25, 50, 75, 100]:
                if pct_before < milestone <= pct_after:
                    from app.infrastructure.external.notification_service import notification_service
                    notification_service.notify_user_from_id(
                        user_id=user_id,
                        title="🏆 ¡Hito alcanzado!",
                        body=f"¡Felicidades! Has completado el {milestone}% de tu álbum.",
                        notif_type="album_milestone",
                    )
                    break
        except Exception:
            pass

    def _build_section_entry(self, key: str, flags_map: dict) -> dict:
        is_special = key in self._SPECIAL_CATEGORIES
        # key is already uppercase for team sections; try uppercase then title-case for flag lookup
        flag = None if is_special else (flags_map.get(key) or flags_map.get(key.title()))
        return {
            "key":      key,
            "label":    key.title() if not is_special else key,
            "type":     "special" if is_special else "team",
            "flagUrl":  flag,
            "stickers": [],
        }

    @staticmethod
    def _finalize_section(sec: dict) -> dict:
        total = len(sec["stickers"])
        owned_n = sum(1 for st in sec["stickers"] if st["owned"])
        sec["total"] = total
        sec["owned_count"] = owned_n
        sec["completion_pct"] = round(owned_n / total * 100, 1) if total else 0
        return sec

    def _get_flags_mapping(self):
        """Returns {DB_team_name → crest_url}.

        DB stores team names as uppercase English (e.g. "ARGENTINA", "SPAIN")
        and 3-letter TLA codes for special stickers (e.g. "ARG", "ESP").
        We build keys for both formats so lookups always hit.
        """
        try:
            from app.infrastructure.external.football_data_service import FootballDataService
            teams_data = FootballDataService().get_teams()
            mapping = {}
            for t in teams_data.get("teams", []):
                crest = t.get("crest")
                if not crest:
                    continue
                name = t.get("name", "")
                tla  = t.get("tla", "")
                if name:
                    mapping[name.upper()] = crest   # e.g. "ARGENTINA"
                if tla:
                    mapping[tla] = crest             # e.g. "ARG"
            return mapping
        except Exception:
            import logging
            logging.exception("Error fetching flags")
            return {}

    def get_album_progress(self, user_id: int) -> Dict[str, Any]:
        from app.domain.models.sticker import Sticker

        # Álbum del usuario (crear si no existe)
        album = Album.query.filter_by(idUser=user_id).first()
        if not album:
            album = Album(idUser=user_id, packBalance=0, coins=0)
            db.session.add(album)
            db.session.commit()

        # Mapa {sticker_id: copies} de láminas poseídas
        owned_rows = (
            db.session.query(sticker_album.c.id_sticker, func.count().label("copies"))
            .filter(sticker_album.c.id_album == album.idAlbum)
            .group_by(sticker_album.c.id_sticker)
            .all()
        )
        owned_map = {row.id_sticker: row.copies for row in owned_rows}

        # Todos los stickers ordenados
        all_stickers = (
            Sticker.query
            .order_by(Sticker.team, Sticker.category, Sticker.paniniCode)
            .all()
        )

        flags_map = self._get_flags_mapping()

        # Teams that have a full album set (have a "Team Crest" sticker)
        proper_teams = {
            s.team.upper()
            for s in Sticker.query.filter_by(category="Team Crest").all()
        }

        sections: Dict[str, dict] = {}
        for s in all_stickers:
            if s.category in self._SPECIAL_CATEGORIES:
                key = s.category
            else:
                key = s.team.upper()  # normalise: "Argentina" → "ARGENTINA"
                if key not in proper_teams:
                    continue  # skip API-only teams
            if key not in sections:
                sections[key] = self._build_section_entry(key, flags_map)
            owned_copies = owned_map.get(s.idSticker, 0)
            sections[key]["stickers"].append({
                "id":          s.idSticker,
                "panini_code": s.paniniCode,
                "name":        s.name,
                "category":    s.category,
                "rarity":      s.rarity,
                "team":        s.team,
                "position":    s.position,
                "nationality": s.nationality,
                "owned":       owned_copies > 0,
                "copies":      owned_copies,
            })

        sections_list = [self._finalize_section(sec) for sec in sections.values()]
        sections_list.sort(key=lambda s: (
            0 if s["type"] == "special" else 1,
            self._SPECIAL_ORDER.get(s["key"], 99) if s["type"] == "special" else s["key"],
        ))

        total_unique      = len(all_stickers)
        total_owned       = len(owned_map)
        repeated_stickers = sum(copies - 1 for copies in owned_map.values() if copies > 1)
        completion        = round(total_owned / total_unique * 100, 2) if total_unique else 0

        # Auto-claim daily packs (same logic as get_user_album)
        self._auto_claim_daily(album)
        db.session.commit()

        collections = [
            {
                "id":      i + 1,
                "name":    sec["label"],
                "count":   sec["owned_count"],
                "flagUrl": sec["flagUrl"],
            }
            for i, sec in enumerate(sections_list)
            if sec["type"] == "team"
        ]

        return {
            "user_id":               user_id,
            "total_owned":           total_owned,
            "total_unique":          total_unique,
            "completion_percentage": completion,
            "pack_balance":          album.packBalance or 0,
            "coins":                 album.coins or 0,
            "repeated_stickers":     repeated_stickers,
            "collections":           collections,
            "sections":              sections_list,
        }
