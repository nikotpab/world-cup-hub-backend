from typing import Optional, List, Dict, Any
from app.application.interfaces.admin_repository import IAdminRepository
from app.domain.models.user import User
from app.domain.models.event import Event
from app.domain.models.notification import Notification
from app.infrastructure.database import db

class SqlAlchemyAdminRepository(IAdminRepository):
    def block_user(self, user_id: int) -> bool:
        user = User.query.get(user_id)
        if not user:
            return False
            
        # Asumimos que podemos agregarle un campo lógico/usar roleId temporal.
        # Simularemos que cambiamos su roleId a 0 (BLOQUEADO) como mecanismo básico antifraude
        user.roleId = 0
        db.session.commit()
        return True

    def get_user_timeline(self, user_id: int) -> List[Dict[str, Any]]:
        # Extrae eventos en la tabla Audit que correspondan a este user_id
        import json
        from app.domain.models.audit import Audit
        audits = Audit.query.order_by(Audit.createdAt.desc(), Audit.idAudit.desc()).all()
        timeline = []
        for a in audits:
            try:
                payload = json.loads(a.payload) if a.payload else {}
                if payload.get("user_id") == user_id or payload.get("userId") == user_id:
                    timeline.append({
                        "eventId": a.idAudit,
                        "type": a.action,
                        "date": a.createdAt.isoformat() if a.createdAt else None,
                        "description": f"{a.action} on {a.affectedEntity} (Result: {a.result})"
                    })
            except Exception:
                pass
        return timeline

    def generate_compliance_report(self) -> List[Dict[str, Any]]:
        # Retorna data agregada anónima para evitar exponer logs sensibles
        users_count = User.query.count()
        return [{"metric": "Total Registros", "value": users_count}]

    def save_news(self, news_data: Dict[str, Any]) -> Any:
        notification = Notification(**news_data)
        db.session.add(notification)
        db.session.commit()
        return {"id": notification.notificationId, "message": notification.message}
