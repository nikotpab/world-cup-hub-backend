from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any

class IMatchRepository(ABC):
    @abstractmethod
    def get_by_id(self, match_id: int) -> Optional[Dict[str, Any]]:
        pass
        
    @abstractmethod
    def get_all(self) -> List[Dict[str, Any]]:
        pass
        
    @abstractmethod
    def get_by_phase(self, phase: str) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    def get_live_matches(self) -> List[Dict[str, Any]]:
        pass
        
    @abstractmethod
    def save(self, match_data: Dict[str, Any]) -> Dict[str, Any]:
        pass
