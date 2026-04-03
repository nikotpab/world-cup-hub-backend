from pydantic import BaseModel, ConfigDict
from datetime import datetime

class MatchCreateDTO(BaseModel):
    status: str
    phase: str
    scheduledAt: datetime
    stadiumId: int
    
    model_config = ConfigDict(extra='forbid')

class MatchResponseDTO(BaseModel):
    matchId: int
    status: str
    phase: str
    scheduledAt: datetime
    stadiumId: int

    model_config = ConfigDict(from_attributes=True)
