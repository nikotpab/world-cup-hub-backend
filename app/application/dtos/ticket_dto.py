from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional, List

class TicketCreateDTO(BaseModel):
    price: float
    matchId: int
    model_config = ConfigDict(extra='forbid')

class TicketReserveDTO(BaseModel):
    userId: int
    matchId: int
    model_config = ConfigDict(extra='forbid')

class TicketPayDTO(BaseModel):
    userId: int
    paymentToken: str
    model_config = ConfigDict(extra='forbid')

class TicketTransferDTO(BaseModel):
    fromUserId: int
    toUserId: int
    model_config = ConfigDict(extra='forbid')

class TicketRefundDTO(BaseModel):
    userId: int
    reason: Optional[str] = "Solicitud de reembolso"
    model_config = ConfigDict(extra='forbid')

class TicketResponseDTO(BaseModel):
    ticketId: int
    status: str
    price: float
    matchId: int
    userId: Optional[int] = None
    reservedAt: Optional[datetime] = None
    expirationDate: Optional[datetime] = None
    paidAt: Optional[datetime] = None
    correlationId: Optional[str] = None
    match_details: Optional[str] = None
    stadium: Optional[str] = None
    date_display: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)

class TicketHistoryItemDTO(BaseModel):
    status: str
    changedAt: datetime
    reason: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)
