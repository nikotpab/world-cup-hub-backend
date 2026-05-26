from typing import List, Dict, Any
from app.application.interfaces.admin_repository import IAdminRepository
from app.application.dtos.admin_dto import NewsCreateDTO, DataSourceUpdateDTO, BlockResponseDTO
from app.infrastructure.cache.redis_client import redis_client
import logging
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


class AdminService:
    def __init__(self, repository: IAdminRepository):
        self.repository = repository

    def block_user(self, user_id: int) -> BlockResponseDTO:
        success = self.repository.block_user(user_id)
        if not success:
            raise ValueError(f"User {user_id} not found")
        logger.warning({"event": "user_blocked", "user_id": user_id,
                        "timestamp": datetime.now(timezone.utc).isoformat()})
        return BlockResponseDTO(user_id=user_id, status="Locked for suspected fraud", blocked=True)

    def unblock_user(self, user_id: int) -> BlockResponseDTO:
        success = self.repository.unblock_user(user_id)
        if not success:
            raise ValueError(f"User {user_id} not found")
        logger.info({"event": "user_unblocked", "user_id": user_id,
                     "timestamp": datetime.now(timezone.utc).isoformat()})
        return BlockResponseDTO(user_id=user_id, status="Account reactivated", blocked=False)

    def flag_user(self, user_id: int, reason: str) -> Dict[str, Any]:
        success = self.repository.flag_user(user_id, reason)
        if not success:
            raise ValueError(f"User {user_id} not found")
        logger.warning({"event": "user_flagged_antifraud", "user_id": user_id, "reason": reason,
                        "timestamp": datetime.now(timezone.utc).isoformat()})
        return {"user_id": user_id, "status": "flagged", "reason": reason}

    def get_flagged_users(self) -> List[Dict[str, Any]]:
        return self.repository.get_flagged_users()

    def get_timeline(self, user_id: int) -> List[Dict[str, Any]]:
        return self.repository.get_user_timeline(user_id)

    def get_compliance_report(self) -> Dict[str, Any]:
        logger.info({"event": "compliance_report_requested",
                     "timestamp": datetime.now(timezone.utc).isoformat()})
        return self.repository.generate_compliance_report()

    def get_audit_log(self, user_id=None, limit: int = 100) -> List[Dict[str, Any]]:
        return self.repository.get_audit_log(user_id=user_id, limit=limit)

    def broadcast_news(self, data: dict) -> dict:
        dto = NewsCreateDTO(**data)
        segment_type  = data.get("segment_type", "global")
        segment_value = data.get("segment_value", "")

        notif_data = {
            "title":            dto.title,
            "message":          dto.message,
            "date":             datetime.now(timezone.utc),
            "notificationType": "GLOBAL_NEWS",
        }

        if segment_type == "global":
            return self.repository.save_news(notif_data)
        return self.repository.save_news_segmented(notif_data, segment_type, str(segment_value))

    def set_active_datasource(self, data: dict):
        dto = DataSourceUpdateDTO(**data)
        if redis_client.client:
            redis_client.set("active_datasource", dto.source)
            logger.info({"event": "datasource_switched", "new_source": dto.source})
            return {"status": f"Switched data origin to {dto.source}"}
        raise RuntimeError("Redis is required to configure Circuit Breaking sources")

    def reactivate_ticket(self, ticket_id: int, ttl_minutes: int = 10) -> Dict[str, Any]:
        result = self.repository.reactivate_ticket(ticket_id, ttl_minutes)
        logger.info({"event": "ticket_reactivated", "ticket_id": ticket_id,
                     "ttl_minutes": ttl_minutes, "timestamp": datetime.now(timezone.utc).isoformat()})
        return result

    def retry_notification(self, history_id: int) -> Dict[str, Any]:
        result = self.repository.retry_notification(history_id)
        logger.info({"event": "notification_retried", "history_id": history_id,
                     "timestamp": datetime.now(timezone.utc).isoformat()})
        return result
