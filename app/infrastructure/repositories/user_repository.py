from typing import Optional, List, Dict, Any
from app.application.interfaces.user_repository import IUserRepository
from app.domain.models.user import User
from app.infrastructure.database import db

class SqlAlchemyUserRepository(IUserRepository):
    def _to_dict(self, user: User) -> Dict[str, Any]:
        if not user:
            return None
        return {
            "userId": user.userId,
            "identification": user.identification,
            "firstName": user.firstName,
            "lastName": user.lastName,
            "email": user.email,
            "registeredAt": user.registeredAt,
            "roleId": user.roleId
        }

    def get_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        user = User.query.get(user_id)
        return self._to_dict(user)

    def get_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        user = User.query.filter_by(email=email).first()
        return self._to_dict(user)

    def save(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        if "userId" in user_data and user_data["userId"]:
            user = User.query.get(user_data["userId"])
            for key, value in user_data.items():
                setattr(user, key, value)
        else:
            user = User(**user_data)
            db.session.add(user)
            
        db.session.commit()
        return self._to_dict(user)

    def get_all(self) -> List[Dict[str, Any]]:
        users = User.query.all()
        return [self._to_dict(user) for user in users]
