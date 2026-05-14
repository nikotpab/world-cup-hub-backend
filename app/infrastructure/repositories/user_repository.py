from typing import Optional, List, Dict, Any
from app.application.interfaces.user_repository import IUserRepository
from app.domain.models.user import User
from app.infrastructure.database import db

class SqlAlchemyUserRepository(IUserRepository):
    def _to_dict(self, user: User) -> Dict[str, Any]:
        if not user:
            return None
        return {
            "userId":           user.idUser,
            "firstName":        user.firstName,
            "lastName":         user.lastName,
            "email":            user.email,
            "password":         user.password,
            "createdAt":        user.createdAt,
            "roleId":           user.idRole,
            "verified":         user.verified,
            "verificationCode": user.verificationCode,
            "accountStatus":    user.accountStatus,
        }

    def get_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        user = User.query.get(user_id)
        return self._to_dict(user)

    def get_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        user = User.query.filter_by(email=email).first()
        return self._to_dict(user)

    # dict key → User model attribute
    _FIELD_MAP = {
        "firstName":        "firstName",
        "lastName":         "lastName",
        "email":            "email",
        "password":         "password",
        "verified":         "verified",
        "verificationCode": "verificationCode",
        "accountStatus":    "accountStatus",
        "roleId":           "idRole",
    }

    def save(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        user_id = user_data.get("userId")
        if user_id:
            user = User.query.get(user_id)
            if not user:
                raise ValueError("Usuario no encontrado")
            for dict_key, attr in self._FIELD_MAP.items():
                if dict_key in user_data:
                    setattr(user, attr, user_data[dict_key])
        else:
            user = User(
                firstName=user_data["firstName"],
                lastName=user_data["lastName"],
                email=user_data["email"],
                password=user_data["password"],
                verified=user_data.get("verified", False),
                verificationCode=user_data.get("verificationCode"),
                idRole=user_data.get("roleId", 2),
            )
            db.session.add(user)
        db.session.commit()
        return self._to_dict(user)

    def get_all(self) -> List[Dict[str, Any]]:
        users = User.query.all()
        return [self._to_dict(user) for user in users]
