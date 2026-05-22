from datetime import datetime, timezone
from flask import Blueprint, request, jsonify
from sqlalchemy import func
from app.application.services.ticket_service import TicketService, RESERVATION_TTL_MINUTES
from app.infrastructure.repositories.ticket_repository import SqlAlchemyTicketRepository
from app.presentation.middlewares.auth import require_role
from app.infrastructure.database import db
from pydantic import ValidationError

ticket_bp = Blueprint('ticket_bp', __name__)

ticket_repo = SqlAlchemyTicketRepository()
ticket_service = TicketService(ticket_repo)

# -----------------------------------------------------------------------
# Consultas
# -----------------------------------------------------------------------

@ticket_bp.route('/tickets', methods=['POST'])
def create_ticket():
    try:
        data = request.get_json()
        result = ticket_service.create_ticket(data)
        return jsonify(result.model_dump()), 201
    except ValidationError as e:
        return jsonify({"error": "ERR_VALIDATION", "details": e.errors()}), 400
    except ValueError as e:
        return jsonify({"error": "ERR_BAD_REQUEST", "message": str(e)}), 400

@ticket_bp.route('/tickets/<int:ticket_id>', methods=['GET'])
def get_ticket(ticket_id):
    try:
        result = ticket_service.get_ticket(ticket_id)
        return jsonify(result.model_dump()), 200
    except ValueError as e:
        return jsonify({"error": "ERR_NOT_FOUND", "message": str(e)}), 404

@ticket_bp.route('/users/<int:user_id>/tickets', methods=['GET'])
def get_user_tickets(user_id):
    results = ticket_service.get_user_tickets(user_id)
    return jsonify([r.model_dump() for r in results]), 200

@ticket_bp.route('/users/<int:user_id>/tickets/daily-stats', methods=['GET'])
def get_user_daily_stats(user_id):
    from app.application.services.ticket_service import MAX_PURCHASES_PER_DAY, MAX_TRANSFERS_PER_DAY
    purchases_today = ticket_repo.count_purchases_today(user_id)
    transfers_today = ticket_repo.count_transfers_today(user_id)
    return jsonify({
        "purchasesToday": purchases_today,
        "maxPurchasesPerDay": MAX_PURCHASES_PER_DAY,
        "transfersToday": transfers_today,
        "maxTransfersPerDay": MAX_TRANSFERS_PER_DAY
    }), 200

@ticket_bp.route('/tickets/<int:ticket_id>/history', methods=['GET'])
def get_ticket_history(ticket_id):
    try:
        result = ticket_service.get_ticket_history(ticket_id)
        return jsonify([r.model_dump() for r in result]), 200
    except ValueError as e:
        return jsonify({"error": "ERR_NOT_FOUND", "message": str(e)}), 404

# -----------------------------------------------------------------------
# Ciclo de vida
# -----------------------------------------------------------------------

@ticket_bp.route('/tickets/reserve', methods=['POST'])
def reserve_ticket():
    """Disponible → Reservada. Body: {userId, matchId}"""
    try:
        result = ticket_service.reserve_ticket(request.get_json())
        return jsonify(result.model_dump()), 200
    except ValidationError as e:
        return jsonify({"error": "ERR_VALIDATION", "details": e.errors()}), 400
    except ValueError as e:
        return jsonify({"error": "ERR_BAD_REQUEST", "message": str(e)}), 400

@ticket_bp.route('/tickets/<int:ticket_id>/pay', methods=['POST'])
def pay_ticket(ticket_id):
    """Reservada → Pagada. Body: {userId, paymentToken}"""
    try:
        result = ticket_service.process_payment(ticket_id, request.get_json())
        # process_payment devuelve un dict con campos datetime — serializamos manualmente
        return jsonify({k: (v.isoformat() if hasattr(v, 'isoformat') else v)
                        for k, v in result.items()}), 200
    except ValidationError as e:
        return jsonify({"error": "ERR_VALIDATION", "details": e.errors()}), 400
    except ValueError as e:
        return jsonify({"error": "ERR_BAD_REQUEST", "message": str(e)}), 400

@ticket_bp.route('/tickets/<int:ticket_id>/transfer', methods=['POST'])
def transfer_ticket(ticket_id):
    """Pagada → Transferida. Body: {fromUserId, toUserId}"""
    try:
        result = ticket_service.transfer_ticket(ticket_id, request.get_json())
        return jsonify(result), 200
    except ValidationError as e:
        return jsonify({"error": "ERR_VALIDATION", "details": e.errors()}), 400
    except ValueError as e:
        return jsonify({"error": "ERR_BAD_REQUEST", "message": str(e)}), 400

@ticket_bp.route('/tickets/<int:ticket_id>/transfer-by-email', methods=['POST'])
def transfer_ticket_by_email(ticket_id):
    """Pagada → Transferida. Body: {fromUserId, toEmail}. Verifica que el destinatario exista."""
    from app.application.dtos.ticket_dto import TicketTransferByEmailDTO
    from app.domain.models.user import User
    try:
        data = request.get_json()
        dto = TicketTransferByEmailDTO(**data)
        recipient = User.query.filter_by(email=dto.toEmail).first()
        if not recipient:
            return jsonify({"error": "ERR_USER_NOT_FOUND",
                            "message": f"No existe ningún usuario con el correo '{dto.toEmail}'."}), 404
        if recipient.idUser == dto.fromUserId:
            return jsonify({"error": "ERR_BAD_REQUEST",
                            "message": "No puedes transferirte una entrada a ti mismo."}), 400
        result = ticket_service.transfer_ticket(ticket_id, {
            "fromUserId": dto.fromUserId,
            "toUserId": recipient.idUser,
        })
        result["toEmail"] = dto.toEmail
        result["toName"] = f"{recipient.firstName} {recipient.lastName}".strip()
        return jsonify(result), 200
    except ValidationError as e:
        return jsonify({"error": "ERR_VALIDATION", "details": e.errors()}), 400
    except ValueError as e:
        return jsonify({"error": "ERR_BAD_REQUEST", "message": str(e)}), 400

@ticket_bp.route('/tickets/<int:ticket_id>/refund', methods=['POST'])
def refund_ticket(ticket_id):
    """Pagada → Reembolsada. Body: {userId, reason?}"""
    try:
        result = ticket_service.refund_ticket(ticket_id, request.get_json())
        return jsonify(result), 200
    except ValidationError as e:
        return jsonify({"error": "ERR_VALIDATION", "details": e.errors()}), 400
    except ValueError as e:
        return jsonify({"error": "ERR_BAD_REQUEST", "message": str(e)}), 400

@ticket_bp.route('/admin/tickets/expire', methods=['POST'])
@require_role([1])
def expire_tickets():
    result = ticket_service.expire_reservations()
    return jsonify(result), 200


# -----------------------------------------------------------------------
# Partidos disponibles para comprar entradas
# -----------------------------------------------------------------------

@ticket_bp.route('/matches/ticketing', methods=['GET'])
def get_ticketing_matches():
    """
    Lista partidos con entradas disponibles (Disponible).
    Devuelve el conteo de disponibles y el precio por partido.
    """
    from app.domain.models.match import Match
    from app.domain.models.ticket import Ticket

    matches = Match.query.filter(
        Match.home_team_name.isnot(None)
    ).order_by(Match.scheduledAt).all()

    result = []
    for m in matches:
        avail = Ticket.query.filter_by(matchId=m.matchId, status='Disponible').count()
        result.append({
            "match_id":   m.matchId,
            "home_name":  m.home_team_name,
            "away_name":  m.away_team_name,
            "date":       m.scheduledAt.isoformat() if m.scheduledAt else None,
            "status":     m.status,
            "price":      m.ticket_price,
            "available":  avail,
        })

    return jsonify({"matches": result}), 200


# -----------------------------------------------------------------------
# Seed de partidos + entradas (admin)
# -----------------------------------------------------------------------

def _parse_match_datetime(date_str: str):
    from datetime import datetime as _dt
    try:
        return _dt.fromisoformat(date_str.replace('Z', '+00:00')).replace(tzinfo=None) if date_str else datetime.now(timezone.utc).replace(tzinfo=None)
    except Exception:
        return datetime.now(timezone.utc).replace(tzinfo=None)


def _ensure_match(match_model, home, away, match_dt, price):
    existing = match_model.query.filter_by(home_team_name=home, away_team_name=away).first()
    if existing:
        return existing, 0
    match_obj = match_model(
        scheduledAt=match_dt,
        home_team_name=home,
        away_team_name=away,
        ticket_price=price,
        status='SCHEDULED',
    )
    db.session.add(match_obj)
    db.session.flush()
    return match_obj, 1



