from flask import Blueprint, request, jsonify
from app.application.services.user_service import UserService
from app.infrastructure.repositories.user_repository import SqlAlchemyUserRepository
from app.infrastructure.database import db
from app.domain.models.user import User
from pydantic import ValidationError

user_bp = Blueprint('user_bp', __name__)

user_repo = SqlAlchemyUserRepository()
user_service = UserService(user_repo)

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
def get_user(user_id):
    try:
        result = user_service.get_user(user_id)
        return jsonify(result.model_dump()), 200
    except ValueError as e:
        return jsonify({"error": "Not Found", "message": str(e)}), 404

@user_bp.route('/users', methods=['GET'])
def get_users():
    results = user_service.get_all_users()
    return jsonify([r.model_dump() for r in results]), 200


@user_bp.route('/users/<int:user_id>/notifications', methods=['GET'])
def get_user_notifications(user_id):
    """Returns the latest notifications for the user."""
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
                "createdAt": n.createdAt.isoformat() if n.createdAt else None
            })
        return jsonify(results), 200
    except Exception as exc:
        return jsonify({"error": "DB error", "details": str(exc)}), 500

@user_bp.route('/users/<int:user_id>/profile-picture', methods=['PUT'])
def update_profile_picture(user_id):
    """Updates the profile picture for a user."""
    data = request.get_json() or {}
    picture = data.get('profilePicture', '')

    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    user.profilePicture = picture
    try:
        db.session.commit()
    except Exception as exc:
        db.session.rollback()
        return jsonify({"error": "DB error", "details": str(exc)}), 500

    return jsonify({"ok": True, "user_id": user_id, "profilePicture": user.profilePicture}), 200


# ── Evidencia de notificaciones (soporte / auditoría) ─────────────────────────
@user_bp.route('/admin/notification-log', methods=['GET'])
def get_notification_log():
    """
    Historial de notificaciones enviadas — para soporte y auditoría.
    Parámetros opcionales: user_id, channel (push|email), notif_type, limit (máx 500).
    """
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

@user_bp.route('/users/<int:user_id>/fcm-token', methods=['POST'])
def update_fcm_token(user_id):
    data = request.get_json() or {}
    token = data.get('token', '').strip()
    if not token:
        return jsonify({"error": "token is required"}), 400

    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    user.fcmToken = token
    try:
        db.session.commit()
    except Exception as exc:
        db.session.rollback()
        return jsonify({"error": "DB error", "details": str(exc)}), 500

    return jsonify({"ok": True, "user_id": user_id}), 200
