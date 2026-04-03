from pydantic import BaseModel, ConfigDict, EmailStr
from typing import Optional
from datetime import datetime

class UserCreateDTO(BaseModel):
    identification: int
    password: str
    firstName: str
    lastName: str
    email: EmailStr
    roleId: int
    
    model_config = ConfigDict(extra='forbid')

class UserResponseDTO(BaseModel):
    userId: int
    identification: int
    firstName: str
    lastName: str
    email: EmailStr
    registeredAt: Optional[datetime] = None
    roleId: int

    model_config = ConfigDict(from_attributes=True)
