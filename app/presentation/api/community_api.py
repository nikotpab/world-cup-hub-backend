from flask import Blueprint, request, jsonify
from app.application.services.community_service import CommunityService
from app.infrastructure.repositories.community_repository import SqlAlchemyCommunityRepository
from app.presentation.middlewares.idempotency import idempotent_request
from pydantic import ValidationError

community_bp = Blueprint('community_bp', __name__)

community_repo = SqlAlchemyCommunityRepository()
community_service = CommunityService(community_repo)

@community_bp.route('/communities', methods=['POST'])
@idempotent_request()
def create_community():
    try:
        data = request.get_json()
        result = community_service.create_community(data)
        return jsonify(result.model_dump()), 201
    except ValidationError as e:
        return jsonify({"error": "ERR_VALIDATION", "details": e.errors()}), 400
    except ValueError as e:
        return jsonify({"error": "ERR_BAD_REQUEST", "message": str(e)}), 400

@community_bp.route('/communities/join', methods=['POST'])
def join_community():
    try:
        data = request.get_json()
        result = community_service.join_community(data)
        return jsonify(result.model_dump()), 200
    except ValidationError as e:
        return jsonify({"error": "ERR_VALIDATION", "details": e.errors()}), 400
    except ValueError as e:
        return jsonify({"error": "ERR_BAD_REQUEST", "message": str(e)}), 400

@community_bp.route('/communities/<int:community_id>/ranking', methods=['GET'])
def get_ranking(community_id):
    try:
        result = community_service.get_ranking(community_id)
        return jsonify([item.model_dump() for item in result]), 200
    except Exception as e:
        return jsonify({"error": "ERR_INTERNAL", "message": str(e)}), 500
