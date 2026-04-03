from typing import List, Dict, Any
from app.application.interfaces.admin_repository import IAdminRepository
from app.application.dtos.admin_dto import NewsCreateDTO, DataSourceUpdateDTO, BlockResponseDTO
from app.infrastructure.cache.redis_client import redis_client
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class AdminService:
    def __init__(self, repository: IAdminRepository):
        self.repository = repository

    def block_user(self, user_id: int) -> BlockResponseDTO:
        success = self.repository.block_user(user_id)
        if not success:
            raise ValueError(f"User {user_id} not found")
            
        logger.warning({"event": "user_blocked_antifraud", "user_id": user_id, "timestamp": datetime.utcnow().isoformat()})
        return BlockResponseDTO(user_id=user_id, status="Locked for suspected fraud", blocked=True)

    def get_timeline(self, user_id: int) -> List[Dict[str, Any]]:
        return self.repository.get_user_timeline(user_id)

    def get_compliance_report(self) -> List[Dict[str, Any]]:
        logger.info({"event": "compliance_report_requested", "timestamp": datetime.utcnow().isoformat()})
        return self.repository.generate_compliance_report()

    def broadcast_news(self, data: dict) -> dict:
        dto = NewsCreateDTO(**data)
        # Adaptar modelo Notification base (simplificado)
        notif_data = {
            "title": dto.title,
            "message": dto.message,
            "date": datetime.utcnow(),
            "notificationType": "GLOBAL_NEWS"
        }
        return self.repository.save_news(notif_data)

    def set_active_datasource(self, data: dict):
        dto = DataSourceUpdateDTO(**data)
        if redis_client.client:
            redis_client.set("active_datasource", dto.source)
            logger.info({"event": "datasource_switched", "new_source": dto.source})
            return {"status": f"Switched data origin to {dto.source}"}
        raise RuntimeError("Redis is required to configure Circuit Breaking sources")
