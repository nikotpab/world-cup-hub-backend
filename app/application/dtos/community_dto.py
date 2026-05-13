from pydantic import BaseModel, ConfigDict

class CommunityCreateDTO(BaseModel):
    name: str
    userId: int # Admin creator

class CommunityJoinDTO(BaseModel):
    invitationCode: int
    userId: int

class CommunityResponseDTO(BaseModel):
    community_id: int
    name: str
    invitation_code: int

    model_config = ConfigDict(from_attributes=True)

class RankingItemDTO(BaseModel):
    userId: int
    name: str
    points: int
