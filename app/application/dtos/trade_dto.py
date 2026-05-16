from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional

class TradeProposeDTO(BaseModel):
    proposer_id: int
    receiver_email: str
    offered_sticker_id: int
    requested_sticker_id: int
    
    model_config = ConfigDict(extra='forbid')

class TradeResponseDTO(BaseModel):
    id: int
    proposer_id: int
    receiver_id: int
    offered_sticker_id: int
    requested_sticker_id: int
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
