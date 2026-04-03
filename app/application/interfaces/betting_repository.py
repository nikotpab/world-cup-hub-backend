from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any

class IBettingRepository(ABC):
    @abstractmethod
    def get_prediction_by_id(self, prediction_id: int) -> Optional[Any]:
        pass
        
    @abstractmethod
    def save_prediction(self, prediction_data: Any) -> Any:
        pass
        
    @abstractmethod
    def flush(self) -> None:
        pass
        
    @abstractmethod
    def commit(self) -> None:
        pass

    @abstractmethod
    def rollback(self) -> None:
        pass
