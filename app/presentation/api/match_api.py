from flask import Blueprint, request, jsonify
from app.application.services.match_service import MatchService
from app.infrastructure.repositories.match_repository import SqlAlchemyMatchRepository
from pydantic import ValidationError

match_bp = Blueprint('match_bp', __name__)

match_repo = SqlAlchemyMatchRepository()
match_service = MatchService(match_repo)

@match_bp.route('/matches', methods=['POST'])
def create_match():
    try:
        data = request.get_json()
        result = match_service.create_match(data)
        return jsonify(result.model_dump()), 201
    except ValidationError as e:
        return jsonify({"error": "Validation Error", "details": e.errors()}), 400
    except ValueError as e:
        return jsonify({"error": "Bad Request", "message": str(e)}), 400

@match_bp.route('/matches/<int:match_id>', methods=['GET'])
def get_match(match_id):
    try:
        result = match_service.get_match(match_id)
        return jsonify(result.model_dump()), 200
    except ValueError as e:
        return jsonify({"error": "Not Found", "message": str(e)}), 404

@match_bp.route('/matches', methods=['GET'])
def get_matches():
    results = match_service.get_all_matches()
    return jsonify([r.model_dump() for r in results]), 200

@match_bp.route('/matches/live', methods=['GET'])
def get_live_matches():
    results = match_service.get_live_matches()
    return jsonify([r.model_dump() for r in results]), 200
