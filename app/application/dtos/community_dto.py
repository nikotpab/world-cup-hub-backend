from pydantic import BaseModel, ConfigDict
from typing import Optional

class CommunityCreateDTO(BaseModel):
    name: str
    userId: int # Admin creator
    maxMembers: Optional[int] = None
    favoriteTeam: Optional[str] = None
    favoritePlayers: Optional[str] = None

class CommunityJoinDTO(BaseModel):
    invitationCode: int
    userId: int

class CommunityResponseDTO(BaseModel):
    idCommunity: int
    name: str
    invitationCode: str
    maxMembers: Optional[int] = None
    favoriteTeam: Optional[str] = None
    favoritePlayers: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class RankingItemDTO(BaseModel):
    userId: int
    name: str
    points: int
