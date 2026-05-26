from flask import Blueprint, request, jsonify, g
from app.application.services.user_service import UserService
from app.infrastructure.repositories.user_repository import SqlAlchemyUserRepository
from app.infrastructure.database import db
from app.domain.models.user import User
from app.presentation.middlewares.auth import require_auth, require_role
from pydantic import ValidationError

user_bp = Blueprint('user_bp', __name__)

_ERR_DB = "DB error"
_ERR_FORBIDDEN = "Forbidden"
_ERR_USER_NOT_FOUND = "User not found"

user_repo = SqlAlchemyUserRepository()
user_service = UserService(user_repo)


def _is_self_or_admin(user_id: int) -> bool:
    return g.user_id == user_id or g.role_id == 1


@user_bp.route('/users', methods=['POST'])
def create_user():
    try:
        data = request.get_json()
        result = user_service.create_user(data)
        return jsonify(result.model_dump()), 201
    except ValidationError as e:
        return jsonify({"error": "Validation Error", "details": e.errors()}), 400
    except ValueError as e:
        return jsonify({"error": "Bad Request", "message": str(e)}), 400


@user_bp.route('/users/<int:user_id>', methods=['GET'])
@require_auth
def get_user(user_id):
    if not _is_self_or_admin(user_id):
        return jsonify({"error": _ERR_FORBIDDEN}), 403
    try:
        result = user_service.get_user(user_id)
        return jsonify(result.model_dump()), 200
    except ValueError as e:
        return jsonify({"error": "Not Found", "message": str(e)}), 404


@user_bp.route('/users', methods=['GET'])
@require_role([1])
def get_users():
    results = user_service.get_all_users()
    return jsonify([r.model_dump() for r in results]), 200


@user_bp.route('/users/<int:user_id>/notifications', methods=['GET'])
@require_auth
def get_user_notifications(user_id):
    if not _is_self_or_admin(user_id):
        return jsonify({"error": _ERR_FORBIDDEN}), 403
    from app.domain.models.notification import Notification
    try:
        notifications = Notification.query.filter_by(userId=user_id).order_by(Notification.createdAt.desc()).limit(20).all()
        results = []
        for n in notifications:
            results.append({
                "id": n.idNotification,
                "title": n.title,
                "message": n.message,
                "notifType": n.notifType,
                "status": n.status or 'sent',
                "createdAt": n.createdAt.isoformat() if n.createdAt else None
            })
        return jsonify(results), 200
    except Exception as exc:
        return jsonify({"error": _ERR_DB, "details": str(exc)}), 500


@user_bp.route('/users/<int:user_id>/notifications/read', methods=['PUT'])
@require_auth
def mark_notifications_read(user_id):
    if not _is_self_or_admin(user_id):
        return jsonify({"error": _ERR_FORBIDDEN}), 403
    from app.domain.models.notification import Notification
    try:
        Notification.query.filter_by(userId=user_id, status='sent').update({Notification.status: 'read'})
        db.session.commit()
        return jsonify({"ok": True}), 200
    except Exception as exc:
        db.session.rollback()
        return jsonify({"error": _ERR_DB, "details": str(exc)}), 500


@user_bp.route('/users/<int:user_id>/profile-picture', methods=['PUT'])
@require_auth
def update_profile_picture(user_id):
    if not _is_self_or_admin(user_id):
        return jsonify({"error": _ERR_FORBIDDEN}), 403
    data = request.get_json() or {}
    picture = data.get('profilePicture', '')
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": _ERR_USER_NOT_FOUND}), 404
    user.profilePicture = picture
    try:
        db.session.commit()
    except Exception as exc:
        db.session.rollback()
        return jsonify({"error": _ERR_DB, "details": str(exc)}), 500
    from app.infrastructure.logger import app_logger
    from datetime import datetime, timezone
    app_logger.info({
        "event": "profile_picture_updated", "user_id": user_id,
        "timestamp": datetime.now(timezone.utc).isoformat(), "audit": True,
    })
    return jsonify({"ok": True, "user_id": user_id, "profilePicture": user.profilePicture}), 200


@user_bp.route('/admin/notification-log', methods=['GET'])
@require_role([1])
def get_notification_log():
    from app.domain.models.notification_history import NotificationHistory
    try:
        limit      = min(int(request.args.get('limit', 100)), 500)
        user_id    = request.args.get('user_id', type=int)
        channel    = request.args.get('channel')
        notif_type = request.args.get('notif_type')
        success    = request.args.get('success')

        q = NotificationHistory.query
        if user_id:
            q = q.filter_by(userId=user_id)
        if channel:
            q = q.filter_by(channel=channel)
        if notif_type:
            q = q.filter_by(notifType=notif_type)
        if success is not None:
            q = q.filter_by(success=success.lower() == 'true')

        entries = q.order_by(NotificationHistory.date.desc()).limit(limit).all()
        return jsonify([{
            "id":             e.idHistory,
            "user_id":        e.userId,
            "channel":        e.channel,
            "recipient":      e.recipient,
            "subject":        e.subject,
            "body":           e.body,
            "success":        e.success,
            "error_msg":      e.error_msg,
            "notif_type":     e.notifType,
            "reference_id":   e.referenceId,
            "reference_type": e.referenceType,
            "date":           e.date.isoformat() if e.date else None,
        } for e in entries]), 200
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


@user_bp.route('/users/<int:user_id>/preferences', methods=['GET'])
@require_auth
def get_user_preferences(user_id):
    if not _is_self_or_admin(user_id):
        return jsonify({"error": _ERR_FORBIDDEN}), 403
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": _ERR_USER_NOT_FOUND}), 404
    return jsonify(user.preferences or {}), 200


@user_bp.route('/users/<int:user_id>/preferences', methods=['PUT'])
@require_auth
def update_user_preferences(user_id):
    if not _is_self_or_admin(user_id):
        return jsonify({"error": _ERR_FORBIDDEN}), 403
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": _ERR_USER_NOT_FOUND}), 404
    data = request.get_json() or {}
    bool_keys = {"notif_push", "notif_email", "notif_trades", "notif_matches", "notif_bets"}
    list_keys = {"favorite_teams", "favorite_cities", "favorite_stadiums"}
    current = dict(user.preferences or {})
    for key, value in data.items():
        if key in bool_keys and isinstance(value, bool):
            current[key] = value
        elif key in list_keys and isinstance(value, list):
            current[key] = [str(v) for v in value if isinstance(v, (str, int))]
    user.preferences = current
    try:
        db.session.commit()
    except Exception as exc:
        db.session.rollback()
        return jsonify({"error": _ERR_DB, "details": str(exc)}), 500
    return jsonify(user.preferences), 200


@user_bp.route('/users/<int:user_id>/fcm-token', methods=['POST'])
@require_auth
def update_fcm_token(user_id):
    if not _is_self_or_admin(user_id):
        return jsonify({"error": _ERR_FORBIDDEN}), 403
    data = request.get_json() or {}
    token = data.get('token', '').strip()
    if not token:
        return jsonify({"error": "token is required"}), 400
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": _ERR_USER_NOT_FOUND}), 404
    user.fcmToken = token
    try:
        db.session.commit()
    except Exception as exc:
        db.session.rollback()
        return jsonify({"error": _ERR_DB, "details": str(exc)}), 500
    return jsonify({"ok": True, "user_id": user_id}), 200
