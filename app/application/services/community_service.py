import secrets
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
        inv_code = str(secrets.randbelow(90000) + 10000)
        
        community = Community(
            name=dto.name,
            invitationCode=inv_code,
            maxMembers=dto.maxMembers,
            favoriteTeam=dto.favoriteTeam,
            favoritePlayers=dto.favoritePlayers,
            description=dto.description,
            icon=dto.icon,
            banner=dto.banner,
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

    def get_user_communities(self, user_id: int) -> List[CommunityResponseDTO]:
        user = self.repository.get_user_by_id(user_id)
        if not user:
            return []
        result = []
        for c in user.communities:
            dto = CommunityResponseDTO.model_validate(c)
            dto.memberCount = len(c.users)
            result.append(dto)
        return result

    def get_suggested_communities(self, user_id: int, limit: int = 10) -> List[CommunityResponseDTO]:
        from app.domain.models.community import Community
        user = self.repository.get_user_by_id(user_id)
        member_ids = {c.idCommunity for c in user.communities} if user else set()
        all_communities = Community.query.order_by(Community.idCommunity.desc()).limit(50).all()
        result = []
        for c in all_communities:
            if c.idCommunity not in member_ids:
                dto = CommunityResponseDTO.model_validate(c)
                dto.memberCount = len(c.users)
                result.append(dto)
            if len(result) >= limit:
                break
        return result

    def get_ranking(self, community_id: int) -> List[RankingItemDTO]:
        ranking_data = self.repository.get_community_ranking(community_id)
        return [RankingItemDTO(**item) for item in ranking_data]
