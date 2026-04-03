from typing import List
from app.application.interfaces.match_repository import IMatchRepository
from app.application.dtos.match_dto import MatchCreateDTO, MatchResponseDTO

class MatchService:
    def __init__(self, repository: IMatchRepository):
        self.repository = repository

    def create_match(self, data: dict) -> MatchResponseDTO:
        dto = MatchCreateDTO(**data)
        saved_match = self.repository.save(dto.model_dump())
        return MatchResponseDTO(**saved_match)

    def get_match(self, match_id: int) -> MatchResponseDTO:
        match = self.repository.get_by_id(match_id)
        if not match:
            raise ValueError("Match not found")
        return MatchResponseDTO(**match)

    def get_all_matches(self) -> List[MatchResponseDTO]:
        matches = self.repository.get_all()
        return [MatchResponseDTO(**m) for m in matches]

    def get_live_matches(self) -> List[MatchResponseDTO]:
        matches = self.repository.get_live_matches()
        return [MatchResponseDTO(**m) for m in matches]

    def update_match_status(self, match_id: int, new_status: str) -> MatchResponseDTO:
        import logging
        from datetime import datetime
        logger = logging.getLogger(__name__)

        match = self.repository.get_by_id(match_id)
        if not match:
            logger.error(f"Error al actualizar estado: Partido {match_id} no encontrado")
            raise ValueError("Partido no encontrado")
            
        old_status = match.get("status")
        match["status"] = new_status
        saved_match = self.repository.save(match)
        
        logger.info({
            "event": "match_status_update",
            "match_id": match_id,
            "old_status": old_status,
            "new_status": new_status,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        return MatchResponseDTO(**saved_match)
