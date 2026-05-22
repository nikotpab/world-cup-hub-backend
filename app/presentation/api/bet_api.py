from flask import Blueprint, request, jsonify
from app.application.services.bet_service import BetService
from app.infrastructure.repositories.bet_repository import SqlAlchemyBetRepository
from app.presentation.middlewares.idempotency import idempotent_request
from pydantic import ValidationError

bet_bp = Blueprint('bet_bp', __name__)

bet_repo = SqlAlchemyBetRepository()
bet_service = BetService(bet_repo)

@bet_bp.route('/bets', methods=['POST'])
@idempotent_request()
def create_bet():
    try:
        data = request.get_json()
        result = bet_service.create_bet(data)
        return jsonify(result.model_dump()), 201
    except ValidationError as e:
        return jsonify({"error": "ERR_VALIDATION", "details": e.errors()}), 400
    except ValueError as e:
        return jsonify({"error": "ERR_BAD_REQUEST", "message": str(e)}), 400

@bet_bp.route('/bets/<int:bet_id>', methods=['PUT', 'PATCH'])
@idempotent_request()
def update_bet(bet_id):
    try:
        data = request.get_json()
        result = bet_service.update_bet(bet_id, data)
        return jsonify(result.model_dump()), 200
    except ValidationError as e:
        return jsonify({"error": "ERR_VALIDATION", "details": e.errors()}), 400
    except RuntimeError as e:
        return jsonify({"error": "ERR_OPTIMISTIC_LOCK_COLLISION", "message": str(e)}), 409
    except ValueError as e:
        return jsonify({"error": "ERR_BAD_REQUEST", "message": str(e)}), 400
