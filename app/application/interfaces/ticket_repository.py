from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any

class ITicketRepository(ABC):
    @abstractmethod
    def get_by_id(self, ticket_id: int) -> Optional[Dict[str, Any]]:
        pass
        
    @abstractmethod
    def get_by_user(self, user_id: int) -> List[Dict[str, Any]]:
        pass
        
    @abstractmethod
    def get_by_match(self, match_id: int) -> List[Dict[str, Any]]:
        pass
        
    @abstractmethod
    def save(self, ticket_data: Dict[str, Any]) -> Dict[str, Any]:
        pass
