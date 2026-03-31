import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

try:
    from src.database import db
    from src.models.ticket import Ticket
except ImportError:
    pass

logger = logging.getLogger(__name__)

class TicketingError(Exception):
    def __init__(self, message: str, status_code: int = 400):
        super().__init__(message)
        self.status_code = status_code

class TicketingService:
    RESERVATION_TTL_MINUTES = 15

    @staticmethod
    def reserve_ticket(match_id: int, user_id: int) -> Ticket:
        try:
            ticket = Ticket.query.filter_by(
                matchId=match_id, status='Disponible'
            ).with_for_update(skip_locked=True).first()

            if not ticket:
                raise TicketingError("No hay entradas disponibles para este partido", 404)

            ticket.status = 'Reservada'
            ticket.userId = user_id
            ticket.reservationDate = datetime.utcnow()
            ticket.expirationDate = datetime.utcnow() + timedelta(minutes=TicketingService.RESERVATION_TTL_MINUTES)
            
            db.session.commit()
            
            logger.info({
                "event": "ticket_reserved",
                "ticket_id": ticket.ticketId,
                "user_id": user_id,
                "expiration": ticket.expirationDate.isoformat()
            })
            
            return ticket
        
        except TicketingError as te:
            db.session.rollback()
            raise te
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error interno reservando ticket: {str(e)}")
            raise TicketingError("Error procesando la reserva", 500)

    @staticmethod
    def _mock_stripe_process_payment(ticket: Ticket, payment_token: str) -> bool:
        if payment_token.startswith("tok_sandbox_fail"):
            return False
        return True

    @staticmethod
    def process_payment(ticket_id: int, user_id: int, payment_token: str) -> Dict[str, Any]:
        ticket = Ticket.query.get(ticket_id)
        
        if not ticket:
            raise TicketingError("Ticket no encontrado", 404)
        
        if ticket.userId != user_id:
            raise TicketingError("El usuario no es titular de esta reserva. Reventa o suplantación prohibida (BR-001)", 403)
        
        if ticket.status != 'Reservada':
            raise TicketingError(f"Estado de entrada inválido para pago: {ticket.status}", 400)
            
        if datetime.utcnow() > ticket.expirationDate:
            raise TicketingError("La reserva ha expirado. Debe realizar una nueva reserva.", 400)

        success = TicketingService._mock_stripe_process_payment(ticket, payment_token)
        
        if not success:
            raise TicketingError("Pago declinado por la pasarela virtual", 402)

        ticket.status = 'Pagada'
        db.session.commit()
        
        logger.info({
            "event": "ticket_paid",
            "ticket_id": ticket_id,
            "user_id": user_id,
            "status": "Pagada",
            "timestamp": datetime.utcnow().isoformat()
        })
        
        return {"success": True, "message": "Pago aprobado. Su entrada ha sido confirmada.", "ticket_id": ticket.ticketId}

    @staticmethod
    def release_expired_tickets() -> int:
        now = datetime.utcnow()
        expired_tickets = Ticket.query.filter(
            Ticket.status == 'Reservada',
            Ticket.expirationDate <= now
        ).all()
        
        count = 0
        for t in expired_tickets:
            t.status = 'Disponible'
            t.userId = None
            t.reservationDate = None
            count += 1
            
            logger.info({
                "event": "ticket_expired",
                "ticket_id": t.ticketId,
                "reason": "TTL expiration limit reached"
            })
            
        db.session.commit()
        return count
