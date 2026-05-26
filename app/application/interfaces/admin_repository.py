from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional


class IAdminRepository(ABC):
    @abstractmethod
    def block_user(self, user_id: int) -> bool:
        pass

    @abstractmethod
    def unblock_user(self, user_id: int) -> bool:
        pass

    @abstractmethod
    def flag_user(self, user_id: int, reason: str) -> bool:
        pass

    @abstractmethod
    def get_user_timeline(self, user_id: int) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    def generate_compliance_report(self) -> Dict[str, Any]:
        pass

    @abstractmethod
    def get_audit_log(self, user_id: Optional[int] = None, limit: int = 100) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    def save_news(self, news_data: Dict[str, Any]) -> Any:
        pass

    @abstractmethod
    def save_news_segmented(self, news_data: Dict[str, Any], segment_type: str, segment_value: str) -> Any:
        pass

    @abstractmethod
    def reactivate_ticket(self, ticket_id: int, ttl_minutes: int) -> Dict[str, Any]:
        pass

    @abstractmethod
    def retry_notification(self, history_id: int) -> Dict[str, Any]:
        pass

    @abstractmethod
    def get_flagged_users(self) -> List[Dict[str, Any]]:
        pass
