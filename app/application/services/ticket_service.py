import uuid
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any
from app.application.interfaces.ticket_repository import ITicketRepository
from app.application.dtos.ticket_dto import (
    TicketCreateDTO, TicketResponseDTO, TicketHistoryItemDTO,
    TicketReserveDTO, TicketPayDTO, TicketTransferDTO, TicketRefundDTO,
)
from app.infrastructure.logger import app_logger

RESERVATION_TTL_MINUTES = 10   # 10 min → libera el cupo si no se paga
MAX_PURCHASES_PER_DAY  = 5
MAX_TRANSFERS_PER_DAY  = 3


class TicketService:
    def __init__(self, repository: ITicketRepository):
        self.repository = repository

    # ------------------------------------------------------------------
    # Consultas
    # ------------------------------------------------------------------

    def create_ticket(self, data: dict) -> TicketResponseDTO:
        """Crea un ticket en estado Disponible (usado por admin/seed)."""
        dto = TicketCreateDTO(**data)
        saved = self.repository.save({"price": dto.price, "matchId": dto.matchId, "status": "Disponible"})
        return TicketResponseDTO(**saved)

    def get_ticket(self, ticket_id: int) -> TicketResponseDTO:
        ticket = self.repository.get_by_id(ticket_id)
        if not ticket:
            raise ValueError("Ticket no encontrado")
        return TicketResponseDTO(**ticket)

    def get_user_tickets(self, user_id: int) -> List[TicketResponseDTO]:
        tickets = self.repository.get_by_user(user_id)
        return [TicketResponseDTO(**t) for t in tickets]

    def get_ticket_history(self, ticket_id: int) -> List[TicketHistoryItemDTO]:
        if not self.repository.get_by_id(ticket_id):
            raise ValueError("Ticket no encontrado")
        rows = self.repository.get_history(ticket_id)
        return [TicketHistoryItemDTO(**r) for r in rows]

    # ------------------------------------------------------------------
    # Ciclo de vida: Disponible → Reservada
    # ------------------------------------------------------------------

    def reserve_ticket(self, data: dict) -> TicketResponseDTO:
        dto = TicketReserveDTO(**data)

        if self.repository.count_purchases_today(dto.userId) >= MAX_PURCHASES_PER_DAY:
            raise ValueError(f"Límite diario de {MAX_PURCHASES_PER_DAY} compras alcanzado")

        ticket = self.repository.get_available_by_match(dto.matchId)
        if not ticket:
            raise ValueError("No hay entradas disponibles para este partido")

        corr_id = str(uuid.uuid4())
        expiration = datetime.utcnow() + timedelta(minutes=RESERVATION_TTL_MINUTES)

        try:
            self.repository.update_ticket(
                ticket,
                status='Reservada',
                userId=dto.userId,
                reservedAt=datetime.utcnow(),
                expirationDate=expiration,
                correlationId=corr_id,
            )
            self.repository.save_history(ticket.ticketId, 'Reservada', 'Reserva iniciada por usuario')
            self.repository.commit()

            app_logger.info({"event": "ticket_reserved", "ticket_id": ticket.ticketId,
                             "user_id": dto.userId, "correlation_id": corr_id, "audit": True})
            return TicketResponseDTO(**self.repository.get_by_id(ticket.ticketId))
        except Exception:
            self.repository.rollback()
            raise

    # ------------------------------------------------------------------
    # Ciclo de vida: Reservada → Pagada
    # ------------------------------------------------------------------

    def process_payment(self, ticket_id: int, data: dict) -> dict:
        dto = TicketPayDTO(**data)
        ticket_data = self.repository.get_by_id(ticket_id)
        if not ticket_data:
            raise ValueError("Ticket no encontrado")
        if ticket_data["status"] != 'Reservada':
            raise ValueError(f"Solo se puede pagar una entrada Reservada (actual: {ticket_data['status']})")
        if ticket_data["userId"] != dto.userId:
            raise ValueError("No eres el titular de esta reserva")
        if ticket_data["expirationDate"] and datetime.now(timezone.utc).replace(tzinfo=None) > ticket_data["expirationDate"]:
            raise ValueError("La reserva ha expirado. Vuelve a intentarlo.")

        from app.domain.models.ticket import Ticket
        from app.infrastructure.external.payment_service import StripePaymentService

        ticket_orm = Ticket.query.get(ticket_id)
        amount_cents = int(float(ticket_data["price"]) * 100)

        try:
            payment_result = StripePaymentService().create_and_confirm_payment(
                amount_cents=amount_cents,
                metadata={"ticket_id": ticket_id, "user_id": dto.userId,
                          "correlation_id": ticket_data["correlationId"]},
            )
            self.repository.save_payment({
                "status":         "completado",
                "amount":         ticket_data["price"],
                "provider":       "stripe",
                "stripeIntentId": payment_result["intent_id"],
                "idUser":         dto.userId,
            })
            self.repository.update_ticket(ticket_orm, status='Pagada', paidAt=datetime.utcnow())
            self.repository.save_history(ticket_id, 'Pagada',
                                         f'Pago Stripe confirmado — intent: {payment_result["intent_id"]}')
            self.repository.commit()

            app_logger.info({"event": "ticket_paid", "ticket_id": ticket_id,
                             "user_id": dto.userId, "stripe_intent": payment_result["intent_id"], "audit": True})

            ticket = self.repository.get_by_id(ticket_id)

            try:
                from app.infrastructure.external.notification_service import notification_service
                match_detail = ticket.get("match_details") or f"Partido #{ticket.get('matchId', '?')}"
                notification_service.notify_user_from_id(
                    user_id=dto.userId,
                    title="🎟️ ¡Compra confirmada!",
                    body=f"Tu entrada para {match_detail} ha sido confirmada. ¡Prepara tus maletas!",
                    notif_type="ticket",
                    reference_id=ticket_id,
                    reference_type="ticket",
                )
            except Exception:
                pass

            return {**TicketResponseDTO(**ticket).model_dump(),
                    "stripe_intent_id": payment_result["intent_id"]}
        except Exception:
            self.repository.rollback()
            raise

    # ------------------------------------------------------------------
    # Ciclo de vida: Pagada → Transferida
    # ------------------------------------------------------------------

    def transfer_ticket(self, ticket_id: int, data: dict) -> Dict[str, Any]:
        dto = TicketTransferDTO(**data)

        if dto.fromUserId == dto.toUserId:
            raise ValueError("No puedes transferirte una entrada a ti mismo")
        if self.repository.count_transfers_today(dto.fromUserId) >= MAX_TRANSFERS_PER_DAY:
            raise ValueError(f"Límite diario de {MAX_TRANSFERS_PER_DAY} transferencias alcanzado")

        ticket_data = self.repository.get_by_id(ticket_id)
        if not ticket_data:
            raise ValueError("Ticket no encontrado")
        if ticket_data["status"] != 'Pagada':
            raise ValueError(f"Solo se pueden transferir entradas Pagadas (actual: {ticket_data['status']})")
        if ticket_data["userId"] != dto.fromUserId:
            raise ValueError("No eres el titular de esta entrada")

        corr_id = str(uuid.uuid4())
        from app.domain.models.ticket import Ticket
        ticket_orm = Ticket.query.get(ticket_id)

        try:
            self.repository.save_transfer({
                "correlationId": corr_id,
                "fromUserId":    dto.fromUserId,
                "toUserId":      dto.toUserId,
                "ticketId":      ticket_id,
            })
            self.repository.update_ticket(ticket_orm, status='Transferida', userId=dto.toUserId,
                                          correlationId=corr_id)
            self.repository.save_history(ticket_id, 'Transferida',
                                         f'Transferido de user {dto.fromUserId} a user {dto.toUserId}')
            self.repository.commit()

            app_logger.info({"event": "ticket_transferred", "ticket_id": ticket_id,
                             "from": dto.fromUserId, "to": dto.toUserId,
                             "correlation_id": corr_id, "audit": True})
            return {"success": True, "correlationId": corr_id,
                    "message": "Entrada transferida correctamente"}
        except Exception:
            self.repository.rollback()
            raise

    # ------------------------------------------------------------------
    # Ciclo de vida: Pagada → Reembolsada
    # ------------------------------------------------------------------

    def refund_ticket(self, ticket_id: int, data: dict) -> Dict[str, Any]:
        dto = TicketRefundDTO(**data)
        ticket_data = self.repository.get_by_id(ticket_id)
        if not ticket_data:
            raise ValueError("Ticket no encontrado")
        if ticket_data["status"] != 'Pagada':
            raise ValueError(f"Solo se pueden reembolsar entradas Pagadas (actual: {ticket_data['status']})")
        if ticket_data["userId"] != dto.userId:
            raise ValueError("No eres el titular de esta entrada")

        from app.domain.models.ticket import Ticket
        ticket_orm = Ticket.query.get(ticket_id)

        try:
            self.repository.update_ticket(ticket_orm, status='Reembolsada')
            self.repository.save_history(ticket_id, 'Reembolsada', dto.reason)
            self.repository.commit()

            app_logger.info({"event": "ticket_refunded", "ticket_id": ticket_id,
                             "user_id": dto.userId, "reason": dto.reason, "audit": True})
            return {"success": True, "message": "Reembolso procesado correctamente"}
        except Exception:
            self.repository.rollback()
            raise

    # ------------------------------------------------------------------
    # Job de expiración: Reservada → Expirada
    # ------------------------------------------------------------------

    def expire_reservations(self) -> Dict[str, Any]:
        expired = self.repository.get_expired_reservations()
        count = 0
        for ticket in expired:
            try:
                self.repository.update_ticket(ticket, status='Expirada')
                self.repository.save_history(ticket.ticketId, 'Expirada',
                                             'TTL de reserva alcanzado — liberado automáticamente')
                self.repository.commit()
                app_logger.info({"event": "ticket_expired", "ticket_id": ticket.ticketId, "audit": True})
                count += 1
            except Exception as e:
                self.repository.rollback()
                app_logger.error({"event": "expire_error", "ticket_id": ticket.ticketId, "details": str(e)})
        return {"expired": count}
