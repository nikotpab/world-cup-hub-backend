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
        return [TicketResponseDTO(**t) for t in tickets]
