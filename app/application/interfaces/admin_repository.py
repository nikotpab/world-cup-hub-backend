from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any

class IAdminRepository(ABC):
    @abstractmethod
    def block_user(self, user_id: int) -> bool:
        pass
        
    @abstractmethod
    def get_user_timeline(self, user_id: int) -> List[Dict[str, Any]]:
        pass
        
    @abstractmethod
    def generate_compliance_report(self) -> List[Dict[str, Any]]:
        pass
        
    @abstractmethod
    def save_news(self, news_data: Dict[str, Any]) -> Any:
        pass
