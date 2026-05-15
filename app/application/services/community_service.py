import random
import logging
from typing import List
from app.application.interfaces.community_repository import ICommunityRepository
from app.application.dtos.community_dto import CommunityCreateDTO, CommunityJoinDTO, CommunityResponseDTO, RankingItemDTO
from app.domain.models.community import Community

logger = logging.getLogger(__name__)

class CommunityService:
    def __init__(self, repository: ICommunityRepository):
        self.repository = repository

    def create_community(self, data: dict) -> CommunityResponseDTO:
        dto = CommunityCreateDTO(**data)
        
        # Generar código de invitación aleatorio (5 dígitos)
        inv_code = str(random.randint(10000, 99999))
        
        community = Community(
            name=dto.name,
            invitationCode=inv_code,
            maxMembers=dto.maxMembers,
            favoriteTeam=dto.favoriteTeam,
            favoritePlayers=dto.favoritePlayers
        )
        
        try:
            user = self.repository.get_user_by_id(dto.userId)
            if not user:
                raise ValueError("Usuario creador no encontrado")
            
            community.users.append(user) # El creador se une automáticamente
            saved_community = self.repository.save_community(community)
            self.repository.commit()
            
            logger.info({"event": "community_created", "community_id": saved_community.idCommunity, "creator": dto.userId})
            return CommunityResponseDTO.model_validate(saved_community)
        except Exception as e:
            self.repository.rollback()
            raise ValueError(f"Error creando comunidad: {str(e)}")

    def join_community(self, data: dict) -> CommunityResponseDTO:
        dto = CommunityJoinDTO(**data)
        
        community = self.repository.get_community_by_code(str(dto.invitationCode))
        if not community:
            raise ValueError("Código de invitación inválido")
            
        user = self.repository.get_user_by_id(dto.userId)
        if not user:
            raise ValueError("Usuario no encontrado")
            
        if user in community.users:
            raise ValueError("Ya eres miembro de esta comunidad")
            
        try:
            community.users.append(user)
            self.repository.commit()
            logger.info({"event": "user_joined_community", "community_id": community.idCommunity, "user_id": dto.userId})
            return CommunityResponseDTO.model_validate(community)
        except Exception as e:
            self.repository.rollback()
            raise ValueError(f"Error al unirse a la comunidad: {str(e)}")

    def get_ranking(self, community_id: int) -> List[RankingItemDTO]:
        ranking_data = self.repository.get_community_ranking(community_id)
        return [RankingItemDTO(**item) for item in ranking_data]
