from typing import List
from app.application.interfaces.ticket_repository import ITicketRepository
from app.application.dtos.ticket_dto import TicketCreateDTO, TicketResponseDTO

class TicketService:
    def __init__(self, repository: ITicketRepository):
        self.repository = repository

    def create_ticket(self, data: dict) -> TicketResponseDTO:
        dto = TicketCreateDTO(**data)
        saved_ticket = self.repository.save(dto.model_dump())
        return TicketResponseDTO(**saved_ticket)

    def get_ticket(self, ticket_id: int) -> TicketResponseDTO:
        ticket = self.repository.get_by_id(ticket_id)
        if not ticket:
            raise ValueError("Ticket not found")
        return TicketResponseDTO(**ticket)

    def get_user_tickets(self, user_id: int) -> List[TicketResponseDTO]:
        tickets = self.repository.get_by_user(user_id)

        # Generar datos provistos por backend para el MVP si la BD está vacía
        if not tickets:
            from datetime import datetime, timedelta
            return [
                TicketResponseDTO(
                    ticketId=1,
                    status="Reservada",
                    price=150.0,
                    expirationDate=datetime.utcnow() + timedelta(days=5),
                    matchId=45,
                    userId=user_id,
                    match_details="Colombia vs Alemania",
                    stadium="Estadio Azteca, CDMX",
                    date_display="15 Jun 2026 - 18:00"
                ),
                TicketResponseDTO(
                    ticketId=2,
                    status="Pagada",
                    price=200.0,
                    expirationDate=datetime.utcnow() + timedelta(days=10),
                    matchId=46,
                    userId=user_id,
                    match_details="Argentina vs España",
                    stadium="Estadio MetLife, CDMX",
                    date_display="18 Jun 2026 - 20:00"
                )
            ]

        return [TicketResponseDTO(**ticket) for ticket in tickets]
