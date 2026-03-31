import logging
from datetime import datetime
from typing import List, Optional
try:
    from src.database import db
    from src.models.match import Match
    from src.models.team import Team
except ImportError:
    pass

logger = logging.getLogger(__name__)

class MatchServiceError(Exception):
    def __init__(self, message: str, status_code: int = 400):
        super().__init__(message)
        self.status_code = status_code

class MatchService:

    @staticmethod
    def get_matches_by_phase(phase: str) -> List[Match]:
        logger.info(f"Buscando partidos para la fase: {phase}")
        matches = Match.query.filter_by(phase=phase).order_by(Match.scheduledAt.asc()).all()
        return matches

    @staticmethod
    def get_upcoming_matches(limit: int = 10) -> List[Match]:
        now = datetime.utcnow()
        logger.info(f"Buscando los próximos {limit} partidos a partir de {now}")
        matches = Match.query.filter(Match.scheduledAt > now).order_by(Match.scheduledAt.asc()).limit(limit).all()
        return matches

    @staticmethod
    def convert_match_time_to_timezone(match_time: datetime, offset_hours: int) -> str:
        import datetime as dt
        local_time = match_time + dt.timedelta(hours=offset_hours)
        return local_time.strftime("%Y-%m-%d %H:%M:%S")

    @staticmethod
    def update_match_status(match_id: int, new_status: str) -> Optional[Match]:
        match = Match.query.get(match_id)
        if not match:
            logger.error(f"Error al actualizar estado: Partido {match_id} no encontrado")
            raise MatchServiceError("Partido no encontrado", 404)
        
        old_status = match.status
        match.status = new_status
        db.session.commit()
        
        logger.info({
            "event": "match_status_update",
            "match_id": match_id,
            "old_status": old_status,
            "new_status": new_status,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        return match
