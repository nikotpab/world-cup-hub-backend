from typing import Optional, List, Dict, Any
from app.domain.models.community import Community
from app.domain.models.user import User

class ICommunityRepository:
    def get_community_by_id(self, community_id: int) -> Optional[Community]:
        raise NotImplementedError

    def get_community_by_code(self, code: int) -> Optional[Community]:
        raise NotImplementedError

    def save_community(self, community: Community) -> Community:
        raise NotImplementedError

    def get_user_by_id(self, user_id: int) -> Optional[User]:
        raise NotImplementedError

    def get_community_ranking(self, community_id: int) -> List[Dict[str, Any]]:
        raise NotImplementedError

    def commit(self) -> None:
        raise NotImplementedError

    def rollback(self) -> None:
        raise NotImplementedError
