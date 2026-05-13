from pydantic import BaseModel, ConfigDict
from typing import Optional

class BetCreateDTO(BaseModel):
    homeGoals: Optional[int] = None
    awayGoals: int
    matchId: int
    userId: int
    
    model_config = ConfigDict(extra='forbid')

class BetUpdateDTO(BaseModel):
    homeGoals: int
    awayGoals: int
    
    model_config = ConfigDict(extra='forbid')

class BetResponseDTO(BaseModel):
    bet_id: int
    home_goals: Optional[int] = None
    away_goals: int
    match_id: int
    user_id: int
    version_id: int

    model_config = ConfigDict(from_attributes=True)
