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
    try:
        data = request.get_json()
        result = admin_service.broadcast_news(data)
        return jsonify(result), 201
    except ValidationError as e:
        return jsonify({"error": "ERR_VALIDATION", "details": e.errors()}), 400

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
