from typing import Optional, List, Dict, Any
from app.application.interfaces.ticket_repository import ITicketRepository
from app.domain.models.ticket import Ticket
from app.infrastructure.database import db

class SqlAlchemyTicketRepository(ITicketRepository):
    def _to_dict(self, ticket: Ticket) -> Dict[str, Any]:
        if not ticket:
            return None
        return {
            "ticketId": ticket.ticketId,
            "status": ticket.status,
            "reservationDate": ticket.reservationDate,
            "expirationDate": ticket.expirationDate,
            "price": ticket.price,
            "matchId": ticket.matchId,
            "userId": ticket.userId
        }

    def get_by_id(self, ticket_id: int) -> Optional[Dict[str, Any]]:
        ticket = Ticket.query.get(ticket_id)
        return self._to_dict(ticket)

    def get_by_user(self, user_id: int) -> List[Dict[str, Any]]:
        tickets = Ticket.query.filter_by(userId=user_id).all()
        return [self._to_dict(t) for t in tickets]

    def get_by_match(self, match_id: int) -> List[Dict[str, Any]]:
        tickets = Ticket.query.filter_by(matchId=match_id).all()
        return [self._to_dict(t) for t in tickets]

    def save(self, ticket_data: Dict[str, Any]) -> Dict[str, Any]:
        if "ticketId" in ticket_data and ticket_data["ticketId"]:
            ticket = Ticket.query.get(ticket_data["ticketId"])
            for key, value in ticket_data.items():
                setattr(ticket, key, value)
        else:
            ticket = Ticket(**ticket_data)
            db.session.add(ticket)
            
        db.session.commit()
        return self._to_dict(ticket)
