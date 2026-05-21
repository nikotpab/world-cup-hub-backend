from pydantic import BaseModel, ConfigDict
from typing import Optional

class CommunityCreateDTO(BaseModel):
    name: str
    userId: int
    maxMembers: Optional[int] = None
    favoriteTeam: Optional[str] = None
    favoritePlayers: Optional[str] = None
    description: Optional[str] = None
    icon: Optional[str] = None
    banner: Optional[str] = None

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
    description: Optional[str] = None
    icon: Optional[str] = None
    banner: Optional[str] = None
    memberCount: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)

class RankingItemDTO(BaseModel):
    userId: int
    name: str
    points: int
