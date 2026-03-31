import logging
from datetime import datetime
import random
from typing import Dict, Any, List

try:
    from src.database import db
    from src.models.prediction import Prediction
    from src.models.match import Match
    from src.models.pack import Pack
    from src.models.sticker import Sticker
    from src.models.album import Album
except ImportError:
    pass

logger = logging.getLogger(__name__)

class GamificationError(Exception):
    def __init__(self, message: str, status_code: int = 400):
        super().__init__(message)
        self.status_code = status_code

class GamificationService:

    @staticmethod
    def _validate_match_time_for_prediction(match: Match) -> None:
        now = datetime.utcnow()
        if now >= match.scheduledAt:
            raise GamificationError("El partido ya ha comenzado. Cierre de pronósticos", 403)

    @staticmethod
    def submit_prediction(match_id: int, user_id: int, home_goals: int, away_goals: int, pool_id: int) -> Prediction:
        match = Match.query.get(match_id)
        if not match:
            raise GamificationError("Partido no encontrado", 404)
        
        GamificationService._validate_match_time_for_prediction(match)
        
        prediction = Prediction.query.filter_by(userId=user_id, matchId=match_id, bettingPoolId=pool_id).first()
        
        if prediction:
            prediction.homeGoals = home_goals
            prediction.awayGoals = away_goals
        else:
            prediction = Prediction(
                homeGoals=home_goals,
                awayGoals=away_goals,
                matchId=match_id,
                userId=user_id,
                bettingPoolId=pool_id
            )
            db.session.add(prediction)
            
        db.session.commit()
        
        logger.info({
            "event": "prediction_submitted",
            "match_id": match_id,
            "user_id": user_id,
            "pool_id": pool_id,
            "home_goals": home_goals,
            "away_goals": away_goals
        })
        
        return prediction

    @staticmethod
    def open_pack(pack_id: int, user_id: int) -> Dict[str, Any]:
        pack = Pack.query.filter_by(packId=pack_id, userId=user_id).first()
        if not pack:
            raise GamificationError("Sobre no encontrado o no pertenece al usuario", 404)
        
        if pack.stickers:
            raise GamificationError("El sobre ya ha sido abierto", 400)
            
        album = Album.query.filter_by(userId=user_id).first()
        if not album:
            album = Album(userId=user_id)
            db.session.add(album)
            db.session.commit()
        
        all_stickers = Sticker.query.all()
        if len(all_stickers) < 5:
            raise GamificationError("No hay suficientes stickers configurados en la Base de Datos", 500)
        
        random_stickers = random.sample(all_stickers, 5)
        
        pack.openedAt = datetime.utcnow()
        for sticker in random_stickers:
            pack.stickers.append(sticker)
            if sticker not in album.stickers:
                album.stickers.append(sticker)
                
        db.session.commit()
        
        logger.info({
            "event": "pack_opened",
            "pack_id": pack_id,
            "user_id": user_id,
            "stickers_found": [s.stickerId for s in random_stickers]
        })
        
        return {
            "success": True,
            "stickers": [{"id": s.stickerId, "name": s.name, "category": s.category} for s in random_stickers]
        }
