from flask import Blueprint, request, jsonify
from app.application.services.trade_service import TradeService
from app.application.services.album_service import AlbumService
from app.infrastructure.repositories.trade_repository import SqlAlchemyTradeRepository
from app.presentation.middlewares.idempotency import idempotent_request
from pydantic import ValidationError

album_bp = Blueprint('album_bp', __name__)

trade_repo = SqlAlchemyTradeRepository()
trade_service = TradeService(trade_repo)
album_service = AlbumService()

@album_bp.route('/users/<int:user_id>/album', methods=['GET'])
def get_user_album(user_id):
    try:
        result = album_service.get_user_album(user_id)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": "ERR_INTERNAL", "message": str(e)}), 500

@album_bp.route('/users/<int:user_id>/packs/open', methods=['POST'])
@idempotent_request()
def open_pack(user_id):
    try:
        result = album_service.open_pack(user_id)
        return jsonify(result), 200
    except ValueError as e:
        return jsonify({"error": "ERR_BAD_REQUEST", "message": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "ERR_INTERNAL", "message": str(e)}), 500

@album_bp.route('/users/<int:user_id>/album/daily-reward', methods=['POST'])
@idempotent_request()
def claim_daily_reward(user_id):
    try:
        result = album_service.claim_daily_reward(user_id)
        return jsonify(result), 200
    except ValueError as e:
        return jsonify({"error": "ERR_BAD_REQUEST", "message": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "ERR_INTERNAL", "message": str(e)}), 500

@album_bp.route('/users/<int:user_id>/album/promo/redeem', methods=['POST'])
def redeem_promo_code(user_id):
    try:
        data = request.get_json()
        code = data.get('code')
        if not code:
            return jsonify({"error": "ERR_BAD_REQUEST", "message": "Código es requerido"}), 400
        result = album_service.redeem_promo_code(user_id, code)
        return jsonify(result), 200
    except ValueError as e:
        return jsonify({"error": "ERR_BAD_REQUEST", "message": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "ERR_INTERNAL", "message": str(e)}), 500

@album_bp.route('/users/<int:user_id>/album/duplicates/convert', methods=['POST'])
def convert_duplicates(user_id):
    try:
        data = request.get_json()
        sticker_ids = data.get('sticker_ids')
        if not sticker_ids:
            return jsonify({"error": "ERR_BAD_REQUEST", "message": "sticker_ids es requerido"}), 400
        result = album_service.convert_duplicate_to_coins(user_id, sticker_ids)
        return jsonify(result), 200
    except ValueError as e:
        return jsonify({"error": "ERR_BAD_REQUEST", "message": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "ERR_INTERNAL", "message": str(e)}), 500

@album_bp.route('/users/<int:user_id>/album/store/buy-pack', methods=['POST'])
@idempotent_request()
def buy_pack(user_id):
    try:
        result = album_service.buy_pack_with_coins(user_id)
        return jsonify(result), 200
    except ValueError as e:
        return jsonify({"error": "ERR_BAD_REQUEST", "message": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "ERR_INTERNAL", "message": str(e)}), 500

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

@album_bp.route('/album/exchange/<int:trade_id>/reject', methods=['PUT'])
def reject_trade(trade_id):
    from app.domain.models.trade_proposal import TradeProposal
    from app.infrastructure.database import db
    trade = TradeProposal.query.get(trade_id)
    if not trade:
        return jsonify({"error": "Trade not found"}), 404
    if trade.status != 'PENDING_CONFIRMATION':
        return jsonify({"error": "ERR_TRADE_CONFLICT", "message": f"Trade is in status: {trade.status}"}), 409
    trade.status = 'REJECTED'
    db.session.commit()
    return jsonify({"id": trade.id, "status": trade.status}), 200

@album_bp.route('/users/<int:user_id>/trades/pending', methods=['GET'])
def get_pending_trades(user_id):
    from app.domain.models.trade_proposal import TradeProposal
    from app.domain.models.sticker import Sticker
    from app.domain.models.user import User
    trades = TradeProposal.query.filter_by(
        receiver_id=user_id, status='PENDING_CONFIRMATION'
    ).order_by(TradeProposal.created_at.desc()).all()
    result = []
    for t in trades:
        offered = Sticker.query.get(t.offered_sticker_id)
        requested = Sticker.query.get(t.requested_sticker_id)
        proposer = User.query.get(t.proposer_id)
        result.append({
            "id": t.id,
            "proposer_email": proposer.email if proposer else None,
            "proposer_name": f"{proposer.firstName} {proposer.lastName}" if proposer else None,
            "offered_sticker": {
                "id": offered.idSticker, "name": offered.name,
                "team": offered.team, "rarity": offered.rarity,
                "photo_url": offered.photoUrl,
            } if offered else None,
            "requested_sticker": {
                "id": requested.idSticker, "name": requested.name,
                "team": requested.team, "rarity": requested.rarity,
                "photo_url": requested.photoUrl,
            } if requested else None,
            "created_at": t.created_at.isoformat() if t.created_at else None,
        })
    return jsonify(result), 200

@album_bp.route('/users/<int:user_id>/album/progress', methods=['GET'])
def get_album_progress(user_id):
    try:
        result = album_service.get_album_progress(user_id)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": "ERR_INTERNAL", "message": str(e)}), 500
