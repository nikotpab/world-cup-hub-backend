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

    @abstractmethod
    def get_available_by_match(self, match_id: int):
        """SELECT FOR UPDATE: devuelve el primer Ticket Disponible para el partido."""
        pass

    @abstractmethod
    def update_ticket(self, ticket, **fields) -> Dict[str, Any]:
        """Aplica los campos dados a la instancia ORM y hace flush (sin commit)."""
        pass

    @abstractmethod
    def save_history(self, ticket_id: int, status: str, reason: str) -> None:
        pass

    @abstractmethod
    def get_history(self, ticket_id: int) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    def save_transfer(self, transfer_data: Dict[str, Any]) -> Dict[str, Any]:
        pass

    @abstractmethod
    def save_payment(self, payment_data: Dict[str, Any]) -> Dict[str, Any]:
        pass

    @abstractmethod
    def count_purchases_today(self, user_id: int) -> int:
        pass

    @abstractmethod
    def count_transfers_today(self, user_id: int) -> int:
        pass

    @abstractmethod
    def get_expired_reservations(self) -> List:
        """Devuelve tickets en estado Reservada cuya expirationDate ya pasó."""
        pass

    @abstractmethod
    def commit(self) -> None:
        pass

    @abstractmethod
    def rollback(self) -> None:
        pass
