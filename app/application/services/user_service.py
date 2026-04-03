from typing import List, Dict, Any
from app.application.interfaces.user_repository import IUserRepository
from app.application.dtos.user_dto import UserCreateDTO, UserResponseDTO

class UserService:
    def __init__(self, repository: IUserRepository):
        self.repository = repository

    def create_user(self, data: dict) -> UserResponseDTO:
        # Pydantic valida la entrada
        dto = UserCreateDTO(**data)
        
        # Guardar en repositorio
        saved_user = self.repository.save(dto.model_dump())
        
        # Devolver DTO de salida
        return UserResponseDTO(**saved_user)

    def get_user(self, user_id: int) -> UserResponseDTO:
        user = self.repository.get_by_id(user_id)
        if not user:
            raise ValueError("User not found")
        return UserResponseDTO(**user)

    def get_all_users(self) -> List[UserResponseDTO]:
        users = self.repository.get_all()
        return [UserResponseDTO(**user) for user in users]
