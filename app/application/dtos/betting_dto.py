from pydantic import BaseModel, ConfigDict
from typing import Optional

class PredictionCreateDTO(BaseModel):
    homeGoals: Optional[int] = None
    awayGoals: int
    bettingPoolId: int
    matchId: int
    userId: int
    
    model_config = ConfigDict(extra='forbid')

class PredictionUpdateDTO(BaseModel):
    homeGoals: int
    awayGoals: int
    
    model_config = ConfigDict(extra='forbid')

class PredictionResponseDTO(BaseModel):
    predictionId: int
    homeGoals: Optional[int] = None
    awayGoals: int
    bettingPoolId: int
    matchId: int
    userId: int
    version_id: int

    model_config = ConfigDict(from_attributes=True)
