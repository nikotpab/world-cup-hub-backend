from pydantic import BaseModel, ConfigDict, model_validator
from datetime import datetime
from typing import Optional, List

class TradeProposeDTO(BaseModel):
    proposer_id: int
    receiver_email: str
    offered_sticker_ids: List[int]   # uno o varios stickers ofrecidos
    requested_sticker_id: int

    model_config = ConfigDict(extra='forbid')

    @model_validator(mode='after')
    def check_at_least_one(self):
        if not self.offered_sticker_ids:
            raise ValueError("Debes ofrecer al menos una lámina.")
        return self


class TradeResponseDTO(BaseModel):
    id: int
    proposer_id: int
    receiver_id: int
    offered_sticker_ids: List[int] = []
    requested_sticker_id: int
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
