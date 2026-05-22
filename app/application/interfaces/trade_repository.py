from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any

class ITradeRepository(ABC):
    @abstractmethod
    def get_by_id(self, trade_id: int) -> Optional[Any]:
        pass
        
    @abstractmethod
    def save(self, trade_data: Any) -> Any:
        pass
        
    @abstractmethod
    def lock_trade(self, trade_id: int) -> Optional[Any]:
        pass

    @abstractmethod
    def commit(self) -> None:
        pass

    @abstractmethod
    def rollback(self) -> None:
        pass
