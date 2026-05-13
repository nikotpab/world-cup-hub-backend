from typing import Optional, List, Dict, Any
from app.domain.models.community import Community
from app.domain.models.user import User

class ICommunityRepository:
    def get_community_by_id(self, community_id: int) -> Optional[Community]:
        pass

    def get_community_by_code(self, code: int) -> Optional[Community]:
        pass

    def save_community(self, community: Community) -> Community:
        pass

    def get_user_by_id(self, user_id: int) -> Optional[User]:
        pass

    def get_community_ranking(self, community_id: int) -> List[Dict[str, Any]]:
        pass

    def commit(self) -> None:
        pass

    def rollback(self) -> None:
        pass
