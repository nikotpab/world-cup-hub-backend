from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional

class TicketCreateDTO(BaseModel):
    status: str
    expirationDate: datetime
    price: float
    matchId: int
    userId: int
    
    model_config = ConfigDict(extra='forbid')

class TicketResponseDTO(BaseModel):
    ticketId: int
    status: str
    reservationDate: Optional[datetime] = None
    expirationDate: datetime
    price: float
    matchId: int
    userId: int

    model_config = ConfigDict(from_attributes=True)
