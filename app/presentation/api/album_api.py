from flask import Blueprint, request, jsonify
from app.application.services.trade_service import TradeService
from app.infrastructure.repositories.trade_repository import SqlAlchemyTradeRepository
from app.presentation.middlewares.idempotency import idempotent_request
from pydantic import ValidationError

album_bp = Blueprint('album_bp', __name__)

trade_repo = SqlAlchemyTradeRepository()
trade_service = TradeService(trade_repo)

@album_bp.route('/album/exchange/propose', methods=['POST'])
@idempotent_request()
def propose_trade():
    try:
        data = request.get_json()
        result = trade_service.propose_trade(data)
        return jsonify(result.model_dump()), 201
    except ValidationError as e:
        return jsonify({"error": "ERR_VALIDATION", "details": e.errors()}), 400
    except ValueError as e:
        return jsonify({"error": "ERR_BAD_REQUEST", "message": str(e)}), 400

@album_bp.route('/album/exchange/<int:trade_id>/confirm', methods=['PUT'])
@idempotent_request()
def confirm_trade(trade_id):
    try:
        result = trade_service.confirm_trade(trade_id)
        return jsonify(result.model_dump()), 200
    except ValueError as e:
        return jsonify({"error": "ERR_TRADE_CONFLICT", "message": str(e)}), 409
