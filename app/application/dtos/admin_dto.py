from pydantic import BaseModel, ConfigDict
from typing import Optional, Dict

class NewsCreateDTO(BaseModel):
    title: str
    message: str
    target_role: Optional[int] = None

class DataSourceUpdateDTO(BaseModel):
    source: str
    endpoint: str

class BlockResponseDTO(BaseModel):
    user_id: int
    status: str
    blocked: bool
