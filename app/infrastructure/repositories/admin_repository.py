import uuid
import logging
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any

from app.application.interfaces.admin_repository import IAdminRepository
from app.domain.models.user import User
from app.domain.models.notification import Notification
from app.infrastructure.database import db

_log = logging.getLogger(__name__)


class SqlAlchemyAdminRepository(IAdminRepository):

    # ------------------------------------------------------------------
    # User management
    # ------------------------------------------------------------------

    def block_user(self, user_id: int) -> bool:
        user = User.query.get(user_id)
        if not user:
            return False
        user.accountStatus = 'bloqueado'
        user.idRole = 0
        db.session.commit()
        return True

    def unblock_user(self, user_id: int) -> bool:
        user = User.query.get(user_id)
        if not user:
            return False
        user.accountStatus = 'activo'
        user.idRole = 2
        db.session.commit()
        return True

    def flag_user(self, user_id: int, reason: str) -> bool:
        user = User.query.get(user_id)
        if not user:
            return False
        user.accountStatus = 'flagged'
        db.session.commit()
        return True

    def get_flagged_users(self) -> List[Dict[str, Any]]:
        users = User.query.filter_by(accountStatus='flagged').all()
        return [
            {
                "user_id": u.idUser,
                "email": u.email,
                "name": f"{u.firstName} {u.lastName}",
                "accountStatus": u.accountStatus,
            }
            for u in users
        ]

    # ------------------------------------------------------------------
    # Timeline
    # ------------------------------------------------------------------

    def get_user_timeline(self, user_id: int) -> List[Dict[str, Any]]:
        import json
        from app.domain.models.audit import Audit
        audits = Audit.query.order_by(Audit.createdAt.desc(), Audit.idAudit.desc()).all()
        timeline = []
        for a in audits:
            try:
                payload = json.loads(a.payload) if a.payload else {}
                if payload.get("user_id") == user_id or payload.get("userId") == user_id:
                    timeline.append({
                        "idAudit": a.idAudit,
                        "correlationId": a.correlationId or "",
                        "createdAt": a.createdAt.isoformat() if a.createdAt else None,
                        "payload": a.payload or "{}",
                        "affectedEntity": a.affectedEntity or "",
                        "action": a.action or "",
                        "result": a.result or "",
                    })
            except Exception as exc:
                _log.debug({"event": "timeline_entry_failed", "details": str(exc)})
        return timeline

    # ------------------------------------------------------------------
    # Audit log (global, optional user filter)
    # ------------------------------------------------------------------

    def get_audit_log(self, user_id=None, limit: int = 100) -> List[Dict[str, Any]]:
        import json
        from app.domain.models.audit import Audit
        query = Audit.query.order_by(Audit.createdAt.desc(), Audit.idAudit.desc())
        if user_id is not None:
            # Filter to events that reference this user in their payload
            all_audits = query.all()
            results = []
            for a in all_audits:
                try:
                    payload = json.loads(a.payload) if a.payload else {}
                    if (payload.get("user_id") == user_id
                            or payload.get("userId") == user_id
                            or payload.get("user_id") == str(user_id)):
                        results.append(a)
                except Exception:
                    pass
                if len(results) >= limit:
                    break
            audits = results
        else:
            audits = query.limit(limit).all()
        return [
            {
                "idAudit": a.idAudit,
                "correlationId": a.correlationId or "",
                "createdAt": a.createdAt.isoformat() if a.createdAt else None,
                "payload": a.payload or "{}",
                "affectedEntity": a.affectedEntity or "",
                "action": a.action or "",
                "result": a.result or "",
            }
            for a in audits
        ]

    # ------------------------------------------------------------------
    # Compliance report
    # ------------------------------------------------------------------

    def generate_compliance_report(self) -> Dict[str, Any]:
        from app.domain.models.ticket import Ticket
        from sqlalchemy import func

        total_users      = User.query.count()
        active_users     = User.query.filter_by(accountStatus='activo').count()
        total_tickets    = Ticket.query.count()
        paid_tickets     = Ticket.query.filter_by(status='Pagada').count()
        reserved_tickets = Ticket.query.filter_by(status='Reservada').count()

        total_revenue = db.session.query(
            func.coalesce(func.sum(Ticket.price), 0)
        ).filter(Ticket.status == 'Pagada').scalar() or 0

        return {
            "total_users": total_users,
            "active_users": active_users,
            "total_tickets": total_tickets,
            "paid_tickets": paid_tickets,
            "reserved_tickets": reserved_tickets,
            "total_revenue": float(total_revenue),
        }

    # ------------------------------------------------------------------
    # Broadcast news
    # ------------------------------------------------------------------

    def save_news(self, news_data: Dict[str, Any]) -> Any:
        notification = Notification(**news_data)
        db.session.add(notification)
        db.session.commit()
        return {"id": notification.notificationId, "message": notification.message}

    def save_news_segmented(
        self, news_data: Dict[str, Any], segment_type: str, segment_value: str
    ) -> Any:
        """Sends broadcast to a subset of users matching segment_type/value.
        segment_type: 'city' | 'match' | 'stadium' | 'global'
        """
        from app.infrastructure.external.notification_service import notification_service
        from app.domain.models.ticket import Ticket

        title   = news_data.get("title", "Notificación")
        message = news_data.get("message", "")
        user_ids: list[int] = []

        if segment_type == "global":
            users = User.query.filter(User.accountStatus == 'activo').all()
            user_ids = [u.idUser for u in users]

        elif segment_type == "city":
            from app.domain.models.stadium import Stadium
            from app.domain.models.city import City
            city = City.query.filter(
                db.func.lower(City.name) == segment_value.lower()
            ).first()
            if city:
                stadiums = Stadium.query.filter_by(cityId=city.cityId).all()
                stadium_ids = [s.stadiumId for s in stadiums]
                from app.domain.models.match import Match
                match_ids_q = db.session.query(Match.matchId).filter(
                    Match.stadiumId.in_(stadium_ids)
                ).all()
                match_ids = [m[0] for m in match_ids_q]
                user_ids = _user_ids_with_tickets_for_matches(match_ids)

        elif segment_type == "match":
            try:
                match_id = int(segment_value)
                user_ids = _user_ids_with_tickets_for_matches([match_id])
            except (ValueError, TypeError):
                pass

        elif segment_type == "stadium":
            from app.domain.models.stadium import Stadium
            from app.domain.models.match import Match
            stadium = Stadium.query.filter(
                db.func.lower(Stadium.name) == segment_value.lower()
            ).first()
            if stadium:
                match_ids_q = db.session.query(Match.matchId).filter_by(
                    stadiumId=stadium.stadiumId
                ).all()
                match_ids = [m[0] for m in match_ids_q]
                user_ids = _user_ids_with_tickets_for_matches(match_ids)

        sent_count = 0
        for uid in set(user_ids):
            try:
                notification_service.notify_user_from_id(
                    user_id=uid,
                    title=title,
                    body=message,
                    notif_type="broadcast",
                )
                sent_count += 1
            except Exception as exc:
                _log.debug({"event": "segmented_broadcast_failed", "user_id": uid, "details": str(exc)})

        return {
            "segment_type": segment_type,
            "segment_value": segment_value,
            "recipients": sent_count,
            "message": message,
        }

    # ------------------------------------------------------------------
    # Ticket reactivation
    # ------------------------------------------------------------------

    def reactivate_ticket(self, ticket_id: int, ttl_minutes: int) -> Dict[str, Any]:
        from app.domain.models.ticket import Ticket
        ticket = Ticket.query.get(ticket_id)
        if not ticket:
            raise ValueError(f"Ticket {ticket_id} no encontrado")
        if ticket.status not in ('Expirada',):
            raise ValueError(f"Solo se pueden reactivar tickets Expirados; estado actual: {ticket.status}")
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        ticket.status = 'Reservada'
        ticket.reservedAt = now
        ticket.expirationDate = now + timedelta(minutes=ttl_minutes)
        ticket.correlationId = str(uuid.uuid4())
        db.session.commit()
        return {
            "ticket_id": ticket_id,
            "status": ticket.status,
            "expiration": ticket.expirationDate.isoformat(),
            "correlation_id": ticket.correlationId,
        }

    # ------------------------------------------------------------------
    # Retry notification
    # ------------------------------------------------------------------

    def retry_notification(self, history_id: int) -> Dict[str, Any]:
        from app.domain.models.notification_history import NotificationHistory
        from app.infrastructure.external.notification_service import notification_service

        entry = NotificationHistory.query.get(history_id)
        if not entry:
            raise ValueError(f"Registro de notificación {history_id} no encontrado")

        if entry.channel == "push":
            result = notification_service.notify_user_from_id(
                user_id=entry.userId,
                title=entry.subject or "",
                body=entry.body or "",
                notif_type=entry.notifType or "retry",
                reference_id=entry.referenceId,
                reference_type=entry.referenceType,
            )
        elif entry.channel == "email":
            result = notification_service.notify_user_from_id(
                user_id=entry.userId,
                title=entry.subject or "",
                body=entry.body or "",
                notif_type=entry.notifType or "retry",
            )
        else:
            raise ValueError(f"Canal desconocido: {entry.channel}")

        return {"history_id": history_id, "channel": entry.channel, "result": str(result)}


def _user_ids_with_tickets_for_matches(match_ids: list[int]) -> list[int]:
    from app.domain.models.ticket import Ticket
    if not match_ids:
        return []
    rows = db.session.query(Ticket.userId).filter(
        Ticket.matchId.in_(match_ids),
        Ticket.userId.isnot(None),
        Ticket.status.in_(('Reservada', 'Pagada')),
    ).distinct().all()
    return [r[0] for r in rows]
