from pydantic import BaseModel, ConfigDict, EmailStr
from typing import Optional
from datetime import datetime

class UserCreateDTO(BaseModel):
    password: str
    firstName: str
    lastName: str
    email: EmailStr
    roleId: Optional[int] = None
    
    model_config = ConfigDict(extra='forbid')

class UserResponseDTO(BaseModel):
    userId: int
    firstName: str
    lastName: str
    email: EmailStr
    registeredAt: Optional[datetime] = None
    roleId: Optional[int] = None
    verified: bool

    model_config = ConfigDict(from_attributes=True)
