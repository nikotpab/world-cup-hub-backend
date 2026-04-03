from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any

class IUserRepository(ABC):
    @abstractmethod
    def get_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        pass

    @abstractmethod
    def get_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        pass
        
    @abstractmethod
    def save(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        pass

    @abstractmethod
    def get_all(self) -> List[Dict[str, Any]]:
        pass
