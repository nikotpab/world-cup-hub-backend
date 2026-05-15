from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime

class MatchCreateDTO(BaseModel):
    status: str = 'SCHEDULED'
    scheduledAt: datetime
    stadiumId: Optional[int] = None
    homeTeamName: Optional[str] = None
    awayTeamName: Optional[str] = None
    ticketPrice: Optional[float] = 150.0

    model_config = ConfigDict(extra='ignore')

class MatchResponseDTO(BaseModel):
    matchId: int
    status: str
    scheduledAt: Optional[str] = None
    stadiumId: Optional[int] = None
    homeTeamName: Optional[str] = None
    awayTeamName: Optional[str] = None
    homeGoals: Optional[int] = 0
    awayGoals: Optional[int] = 0
    ticketPrice: Optional[float] = 150.0

    model_config = ConfigDict(from_attributes=True)
