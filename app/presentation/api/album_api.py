from flask import Blueprint, request, jsonify, g
from app.application.services.trade_service import TradeService
from app.application.services.album_service import AlbumService
from app.infrastructure.repositories.trade_repository import SqlAlchemyTradeRepository
from app.presentation.middlewares.auth import require_auth
from app.presentation.middlewares.idempotency import idempotent_request
from pydantic import ValidationError

album_bp = Blueprint('album_bp', __name__)

trade_repo = SqlAlchemyTradeRepository()
trade_service = TradeService(trade_repo)
album_service = AlbumService()

_ERR_FORBIDDEN = "Forbidden"


def _is_self_or_admin(user_id: int) -> bool:
    return g.user_id == user_id or g.role_id == 1


@album_bp.route('/users/<int:user_id>/album', methods=['GET'])
@require_auth
def get_user_album(user_id):
    if not _is_self_or_admin(user_id):
        return jsonify({"error": _ERR_FORBIDDEN}), 403
    try:
        result = album_service.get_user_album(user_id)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": "ERR_INTERNAL", "message": str(e)}), 500


@album_bp.route('/users/<int:user_id>/packs/open', methods=['POST'])
@require_auth
@idempotent_request()
def open_pack(user_id):
    if not _is_self_or_admin(user_id):
        return jsonify({"error": _ERR_FORBIDDEN}), 403
    try:
        result = album_service.open_pack(user_id)
        return jsonify(result), 200
    except ValueError as e:
        return jsonify({"error": "ERR_BAD_REQUEST", "message": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "ERR_INTERNAL", "message": str(e)}), 500


@album_bp.route('/users/<int:user_id>/album/promo/redeem', methods=['POST'])
@require_auth
def redeem_promo_code(user_id):
    if not _is_self_or_admin(user_id):
        return jsonify({"error": _ERR_FORBIDDEN}), 403
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
@require_auth
def convert_duplicates(user_id):
    if not _is_self_or_admin(user_id):
        return jsonify({"error": _ERR_FORBIDDEN}), 403
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
@require_auth
@idempotent_request()
def buy_pack(user_id):
    if not _is_self_or_admin(user_id):
        return jsonify({"error": _ERR_FORBIDDEN}), 403
    try:
        result = album_service.buy_pack_with_coins(user_id)
        return jsonify(result), 200
    except ValueError as e:
        return jsonify({"error": "ERR_BAD_REQUEST", "message": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "ERR_INTERNAL", "message": str(e)}), 500


@album_bp.route('/album/exchange/propose', methods=['POST'])
@require_auth
@idempotent_request()
def propose_trade():
    try:
        data = request.get_json()
        # Enforce that proposer_id matches the authenticated user
        if data.get('proposer_id') != g.user_id and g.role_id != 1:
            return jsonify({"error": _ERR_FORBIDDEN}), 403
        result = trade_service.propose_trade(data)
        return jsonify(result.model_dump()), 201
    except ValidationError as e:
        return jsonify({"error": "ERR_VALIDATION", "details": e.errors()}), 400
    except ValueError as e:
        return jsonify({"error": "ERR_BAD_REQUEST", "message": str(e)}), 400


@album_bp.route('/album/exchange/<int:trade_id>/confirm', methods=['PUT'])
@require_auth
@idempotent_request()
def confirm_trade(trade_id):
    try:
        result = trade_service.confirm_trade(trade_id)
        return jsonify(result.model_dump()), 200
    except ValueError as e:
        return jsonify({"error": "ERR_TRADE_CONFLICT", "message": str(e)}), 409


@album_bp.route('/album/exchange/<int:trade_id>/reject', methods=['PUT'])
@require_auth
def reject_trade(trade_id):
    from app.domain.models.trade_proposal import TradeProposal
    from app.infrastructure.database import db
    trade = TradeProposal.query.get(trade_id)
    if not trade:
        return jsonify({"error": "Trade not found"}), 404
    # Only the receiver or an admin can reject
    if trade.receiver_id != g.user_id and g.role_id != 1:
        return jsonify({"error": _ERR_FORBIDDEN}), 403
    if trade.status != 'PENDING_CONFIRMATION':
        return jsonify({"error": "ERR_TRADE_CONFLICT", "message": f"Trade is in status: {trade.status}"}), 409
    trade.status = 'REJECTED'
    db.session.commit()

    try:
        from app.infrastructure.external.notification_service import notification_service
        notification_service.notify_user_from_id(
            user_id=trade.proposer_id,
            title="Intercambio rechazado",
            body="Tu propuesta de intercambio fue rechazada por el otro usuario.",
            notif_type="trade_rejected",
            reference_id=trade.id,
            reference_type="trade_proposal",
        )
    except Exception:
        pass

    return jsonify({"id": trade.id, "status": trade.status}), 200


@album_bp.route('/users/<int:user_id>/trades/pending', methods=['GET'])
@require_auth
def get_pending_trades(user_id):
    if not _is_self_or_admin(user_id):
        return jsonify({"error": _ERR_FORBIDDEN}), 403
    from app.domain.models.trade_proposal import TradeProposal
    from app.domain.models.sticker import Sticker
    from app.domain.models.user import User
    trades = TradeProposal.query.filter_by(
        receiver_id=user_id, status='PENDING_CONFIRMATION'
    ).order_by(TradeProposal.created_at.desc()).all()
    result = []
    from app.infrastructure.database import db as _db
    for t in trades:
        offered_ids = t.offered_sticker_ids or []
        if not offered_ids:
            row = _db.session.execute(
                _db.text("SELECT offered_sticker_id FROM trade_proposal WHERE id = :id"),
                {"id": t.id}
            ).fetchone()
            if row and row[0]:
                offered_ids = [row[0]]
        offered_stickers = []
        for sid in offered_ids:
            s = Sticker.query.get(sid)
            if s:
                offered_stickers.append({
                    "id": s.idSticker, "name": s.name,
                    "team": s.team, "rarity": s.rarity,
                    "photo_url": s.photoUrl,
                })
        requested = Sticker.query.get(t.requested_sticker_id)
        proposer = User.query.get(t.proposer_id)
        result.append({
            "id": t.id,
            "proposer_email": proposer.email if proposer else None,
            "proposer_name": f"{proposer.firstName} {proposer.lastName}" if proposer else None,
            "offered_stickers": offered_stickers,
            "requested_sticker": {
                "id": requested.idSticker, "name": requested.name,
                "team": requested.team, "rarity": requested.rarity,
                "photo_url": requested.photoUrl,
            } if requested else None,
            "created_at": t.created_at.isoformat() if t.created_at else None,
        })
    return jsonify(result), 200


@album_bp.route('/users/<int:user_id>/album/progress', methods=['GET'])
@require_auth
def get_album_progress(user_id):
    if not _is_self_or_admin(user_id):
        return jsonify({"error": _ERR_FORBIDDEN}), 403
    try:
        result = album_service.get_album_progress(user_id)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": "ERR_INTERNAL", "message": str(e)}), 500
