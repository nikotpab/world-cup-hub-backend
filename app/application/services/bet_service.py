from datetime import datetime, timedelta, date, timezone
import logging
from sqlalchemy.orm.exc import StaleDataError
from app.application.interfaces.bet_repository import IBetRepository
from app.application.dtos.bet_dto import BetCreateDTO, BetUpdateDTO, BetResponseDTO
from app.domain.models.bet import Bet
from app.domain.models.album import Album
from app.infrastructure.database import db

logger = logging.getLogger(__name__)

class BetService:
    def __init__(self, repository: IBetRepository):
        self.repository = repository

    def create_bet(self, data: dict) -> BetResponseDTO:
        dto = BetCreateDTO(**data)
        
        # Regla de Cierre: Verificar si el partido ya empezó o está por empezar (bloqueo 15 min antes)
        match = self.repository.get_match_by_id(dto.matchId)
        if not match:
            raise ValueError("Partido no encontrado")
            
        if datetime.now(timezone.utc).replace(tzinfo=None) > (match.scheduledAt - timedelta(minutes=15)):
            raise ValueError("El tiempo para realizar pronósticos ha expirado para este partido")

        try:
            # Evidencia Auditada: Verificar si ya existe un pronóstico para este usuario en este partido
            existing = self.repository.get_bet_by_user_match(dto.userId, dto.matchId)
            if existing:
                raise ValueError("Ya has registrado un pronóstico para este partido")

            bet = Bet(
                home_goals=dto.homeGoals,
                away_goals=dto.awayGoals,
                match_id=dto.matchId,
                user_id=dto.userId
            )
            saved_bet = self.repository.save_bet(bet)
            
            # --- Catalyst Rule: Reward a pack for the first prediction of the day ---
            today_start = datetime.combine(date.today(), datetime.min.time())
            daily_bets_count = Bet.query.filter(
                Bet.user_id == dto.userId, 
                Bet.createdAt >= today_start
            ).count()
            
            if daily_bets_count == 0:
                album = Album.query.filter_by(userId=dto.userId).first()
                if not album:
                    album = Album(userId=dto.userId, packBalance=0, coins=0)
                    db.session.add(album)
                
                if album.packBalance is None: album.packBalance = 0
                
                album.packBalance += 1
            
            self.repository.commit()
            
            try:
                from app.infrastructure.external.notification_service import notification_service
                notification_service.notify_user_from_id(
                    user_id=dto.userId,
                    title="⚽ ¡Pronóstico Registrado!",
                    body=f"Tu pronóstico para el partido ha sido confirmado de forma exitosa. ¡Mucha suerte!",
                    notif_type="bet",
                    reference_id=saved_bet.bet_id,
                    reference_type="bet"
                )
            except Exception as e:
                logger.error({"event": "bet_notification_error", "details": str(e)})
            
            logger.info({
                "event": "bet_created", 
                "bet_id": saved_bet.bet_id,
                "user_id": dto.userId,
                "audit": True
            })
            
            response = BetResponseDTO.model_validate(saved_bet)
            # Note: The DTO might not have a message field, but we can log it or handle it in the response if needed.
            # For now, we'll just ensure the logic runs.
            return response
            
        except Exception as e:
            self.repository.rollback()
            raise ValueError(f"No se pudo registrar la apuesta: {str(e)}")

    def update_bet(self, bet_id: int, data: dict) -> BetResponseDTO:
        dto = BetUpdateDTO(**data)
        
        try:
            bet = self.repository.get_bet_by_id(bet_id)
            if not bet:
                raise ValueError("Bet not found")
            
            # Regla de Cierre: Verificar tiempo antes de actualizar
            match = self.repository.get_match_by_id(bet.match_id)
            if datetime.now(timezone.utc).replace(tzinfo=None) > (match.scheduledAt - timedelta(minutes=15)):
                raise ValueError("Ya no es posible modificar este pronóstico")
                
            bet.home_goals = dto.homeGoals
            bet.away_goals = dto.awayGoals
            
            self.repository.flush()
            self.repository.commit()
            return BetResponseDTO.model_validate(bet)
            
        except StaleDataError:
            self.repository.rollback()
            logger.warning({"event": "optimistic_lock_collision", "bet_id": bet_id})
            raise RuntimeError("Collision detected. La apuesta ha sido modificada por otra transacción. Refresca y reintenta.")
        except Exception as e:
            self.repository.rollback()
            raise ValueError(f"Error actualizando pronóstico: {str(e)}")
