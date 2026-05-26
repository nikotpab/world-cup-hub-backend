from flask import Blueprint, request, jsonify
from app.application.services.admin_service import AdminService
from app.infrastructure.repositories.admin_repository import SqlAlchemyAdminRepository
from app.presentation.middlewares.auth import require_role
from pydantic import ValidationError

admin_bp = Blueprint('admin_bp', __name__)

admin_repo = SqlAlchemyAdminRepository()
admin_service = AdminService(admin_repo)


@admin_bp.route('/admin/users/<int:user_id>/block', methods=['POST'])
@require_role([1])
def block_user(user_id):
    try:
        result = admin_service.block_user(user_id)
        return jsonify(result.model_dump()), 200
    except ValueError as e:
        return jsonify({"error": "ERR_NOT_FOUND", "message": str(e)}), 404


@admin_bp.route('/admin/users/<int:user_id>/unblock', methods=['POST'])
@require_role([1])
def unblock_user(user_id):
    try:
        result = admin_service.unblock_user(user_id)
        return jsonify(result.model_dump()), 200
    except ValueError as e:
        return jsonify({"error": "ERR_NOT_FOUND", "message": str(e)}), 404


@admin_bp.route('/admin/users/<int:user_id>/flag', methods=['POST'])
@require_role([1])
def flag_user(user_id):
    data = request.get_json() or {}
    reason = data.get("reason", "Manual flag by admin")
    try:
        result = admin_service.flag_user(user_id, reason)
        return jsonify(result), 200
    except ValueError as e:
        return jsonify({"error": "ERR_NOT_FOUND", "message": str(e)}), 404


@admin_bp.route('/admin/users/flagged', methods=['GET'])
@require_role([1])
def get_flagged_users():
    results = admin_service.get_flagged_users()
    return jsonify(results), 200


@admin_bp.route('/admin/users/<int:user_id>/timeline', methods=['GET'])
@require_role([1])
def get_timeline(user_id):
    results = admin_service.get_timeline(user_id)
    return jsonify(results), 200


@admin_bp.route('/admin/reports/compliance', methods=['GET'])
@require_role([1])
def get_compliance_report():
    results = admin_service.get_compliance_report()
    return jsonify(results), 200


@admin_bp.route('/admin/news', methods=['POST'])
@require_role([1])
def broadcast_news():
    """
    Broadcast a news/notification message.
    Optional body fields:
      segment_type:  'global' (default) | 'city' | 'match' | 'stadium'
      segment_value: city name, match ID, or stadium name
    """
    try:
        data = request.get_json()
        result = admin_service.broadcast_news(data)
        return jsonify(result), 201
    except ValidationError as e:
        return jsonify({"error": "ERR_VALIDATION", "details": e.errors()}), 400


@admin_bp.route('/admin/tickets/<int:ticket_id>/reactivate', methods=['POST'])
@require_role([1])
def reactivate_ticket(ticket_id):
    """Reactivates an expired ticket for support purposes."""
    data = request.get_json() or {}
    ttl_minutes = int(data.get("ttl_minutes", 10))
    try:
        result = admin_service.reactivate_ticket(ticket_id, ttl_minutes)
        return jsonify(result), 200
    except ValueError as e:
        return jsonify({"error": "ERR_BAD_REQUEST", "message": str(e)}), 400


@admin_bp.route('/admin/notifications/<int:history_id>/retry', methods=['POST'])
@require_role([1])
def retry_notification(history_id):
    """Retries a previously failed notification."""
    try:
        result = admin_service.retry_notification(history_id)
        return jsonify(result), 200
    except ValueError as e:
        return jsonify({"error": "ERR_NOT_FOUND", "message": str(e)}), 404


@admin_bp.route('/admin/email-test', methods=['POST'])
@require_role([1])
def test_email():
    data = request.get_json() or {}
    to_email = data.get('to', '').strip()
    if not to_email:
        return jsonify({"error": "ERR_BAD_REQUEST", "message": "El campo 'to' es requerido"}), 400
    from app.infrastructure.external.email_service import SmtpEmailService
    try:
        svc = SmtpEmailService()
        result = svc.send_email(
            to_email,
            "Prueba SMTP - World Cup Hub",
            "<p>La conexion SMTP esta configurada correctamente.</p>",
        )
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": "ERR_SMTP", "message": str(e)}), 500


@admin_bp.route('/admin/audit-log', methods=['GET'])
@require_role([1])
def get_audit_log():
    user_id_str = request.args.get('user_id')
    limit = int(request.args.get('limit', 100))
    user_id = int(user_id_str) if user_id_str and user_id_str.isdigit() else None
    results = admin_service.get_audit_log(user_id=user_id, limit=limit)
    return jsonify(results), 200


@admin_bp.route('/admin/settings/datasource', methods=['PUT'])
@require_role([1])
def set_data_source():
    try:
        data = request.get_json()
        result = admin_service.set_active_datasource(data)
        return jsonify(result), 200
    except ValidationError as e:
        return jsonify({"error": "ERR_VALIDATION", "details": e.errors()}), 400
    except RuntimeError as e:
        return jsonify({"error": "ERR_CONFIG_STATE", "message": str(e)}), 503
