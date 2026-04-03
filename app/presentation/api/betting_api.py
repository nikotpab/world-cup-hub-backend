from flask import Blueprint, request, jsonify
from app.application.services.betting_service import BettingService
from app.infrastructure.repositories.betting_repository import SqlAlchemyBettingRepository
from app.presentation.middlewares.idempotency import idempotent_request
from pydantic import ValidationError

betting_bp = Blueprint('betting_bp', __name__)

betting_repo = SqlAlchemyBettingRepository()
betting_service = BettingService(betting_repo)

@betting_bp.route('/pools/<int:pool_id>/predictions', methods=['POST'])
@idempotent_request()
def create_prediction(pool_id):
    try:
        data = request.get_json()
        data['bettingPoolId'] = pool_id
        result = betting_service.create_prediction(data)
        return jsonify(result.model_dump()), 201
    except ValidationError as e:
        return jsonify({"error": "ERR_VALIDATION", "details": e.errors()}), 400
    except ValueError as e:
        return jsonify({"error": "ERR_BAD_REQUEST", "message": str(e)}), 400

@betting_bp.route('/predictions/<int:prediction_id>', methods=['PUT', 'PATCH'])
@idempotent_request()
def update_prediction(prediction_id):
    try:
        data = request.get_json()
        result = betting_service.update_prediction(prediction_id, data)
        return jsonify(result.model_dump()), 200
    except ValidationError as e:
        return jsonify({"error": "ERR_VALIDATION", "details": e.errors()}), 400
    except RuntimeError as e:
        return jsonify({"error": "ERR_OPTIMISTIC_LOCK_COLLISION", "message": str(e)}), 409
    except ValueError as e:
        return jsonify({"error": "ERR_BAD_REQUEST", "message": str(e)}), 400
