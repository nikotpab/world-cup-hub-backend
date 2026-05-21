from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from app.application.interfaces.ticket_repository import ITicketRepository
from app.domain.models.ticket import Ticket
from app.domain.models.ticket_history import TicketHistory
from app.domain.models.transfer import Transfer
from app.domain.models.payment import Payment
from app.infrastructure.database import db

class SqlAlchemyTicketRepository(ITicketRepository):

    def _to_dict(self, ticket: Ticket) -> Optional[Dict[str, Any]]:
        if not ticket:
            return None
        return {
            "ticketId":       ticket.ticketId,
            "status":         ticket.status,
            "price":          float(ticket.price) if ticket.price else None,
            "matchId":        ticket.matchId,
            "userId":         ticket.userId,
            "reservedAt":     ticket.reservedAt,
            "expirationDate": ticket.expirationDate,
            "paidAt":         ticket.paidAt,
            "correlationId":  ticket.correlationId,
        }

    def get_by_id(self, ticket_id: int) -> Optional[Dict[str, Any]]:
        return self._to_dict(Ticket.query.get(ticket_id))

    def get_by_user(self, user_id: int) -> List[Dict[str, Any]]:
        return [self._to_dict(t) for t in Ticket.query.filter_by(userId=user_id).all()]

    def get_by_match(self, match_id: int) -> List[Dict[str, Any]]:
        return [self._to_dict(t) for t in Ticket.query.filter_by(matchId=match_id).all()]

    def save(self, ticket_data: Dict[str, Any]) -> Dict[str, Any]:
        if ticket_data.get("ticketId"):
            ticket = Ticket.query.get(ticket_data["ticketId"])
            for key, value in ticket_data.items():
                setattr(ticket, key, value)
        else:
            ticket = Ticket(**ticket_data)
            db.session.add(ticket)
        db.session.commit()
        return self._to_dict(ticket)

    def get_available_by_match(self, match_id: int) -> Optional[Ticket]:
        return (
            Ticket.query
            .filter_by(matchId=match_id, status='Disponible')
            .with_for_update()
            .first()
        )

    def update_ticket(self, ticket: Ticket, **fields) -> Dict[str, Any]:
        for key, value in fields.items():
            setattr(ticket, key, value)
        db.session.flush()
        return self._to_dict(ticket)

    def save_history(self, ticket_id: int, status: str, reason: str) -> None:
        entry = TicketHistory(idTicket=ticket_id, status=status, reason=reason)
        db.session.add(entry)

    def get_history(self, ticket_id: int) -> List[Dict[str, Any]]:
        rows = TicketHistory.query.filter_by(idTicket=ticket_id).order_by(TicketHistory.changedAt).all()
        return [{"status": r.status, "changedAt": r.changedAt, "reason": r.reason} for r in rows]

    def save_transfer(self, transfer_data: Dict[str, Any]) -> Dict[str, Any]:
        transfer = Transfer(**transfer_data)
        db.session.add(transfer)
        db.session.flush()
        return {"idTransfer": transfer.idTransfer, "correlationId": transfer.correlationId}

    def save_payment(self, payment_data: Dict[str, Any]) -> Dict[str, Any]:
        payment = Payment(**payment_data)
        db.session.add(payment)
        db.session.flush()
        return {"idPayment": payment.idPayment, "status": payment.status}

    def count_purchases_today(self, user_id: int) -> int:
        today = datetime.now(timezone.utc).date()
        return (
            Ticket.query
            .filter(Ticket.userId == user_id, Ticket.status == 'Pagada',
                    db.func.date(Ticket.paidAt) == today)
            .count()
        )

    def count_transfers_today(self, user_id: int) -> int:
        today = datetime.now(timezone.utc).date()
        return (
            Transfer.query
            .filter(Transfer.fromUserId == user_id,
                    db.func.date(Transfer.transferDate) == today)
            .count()
        )

    def get_expired_reservations(self) -> List[Ticket]:
        return (
            Ticket.query
            .filter(Ticket.status == 'Reservada', Ticket.expirationDate < datetime.now(timezone.utc).replace(tzinfo=None))
            .all()
        )

    def commit(self) -> None:
        db.session.commit()

    def rollback(self) -> None:
        db.session.rollback()
