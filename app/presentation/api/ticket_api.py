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

@ticket_bp.route('/admin/tickets/seed', methods=['POST'])
@require_role([1])
def seed_tickets():
    """
    Crea partidos con datos reales del API de football-data.org
    y genera N entradas Disponibles por partido.
    Query param: tickets_per_match (default 30)
    """
    from app.domain.models.match import Match
    from app.domain.models.ticket import Ticket, VALID_STATUSES
    from app.infrastructure.external.football_data_service import FootballDataService
    from datetime import timezone as tz

    n = int(request.args.get('tickets_per_match', 30))
    svc = FootballDataService()
    raw = svc.get_upcoming_matches()
    matches_data = raw.get('matches', [])[:15]

    created_matches = 0
    created_tickets = 0

    price_tiers = [120.0, 150.0, 200.0, 280.0, 350.0]

    for i, m in enumerate(matches_data):
        home = (m.get('homeTeam') or {}).get('shortName') or (m.get('homeTeam') or {}).get('name', 'Local')
        away = (m.get('awayTeam') or {}).get('shortName') or (m.get('awayTeam') or {}).get('name', 'Visitante')
        date_str = m.get('utcDate')
        try:
            from datetime import datetime as _dt
            match_dt = _dt.fromisoformat(date_str.replace('Z', '+00:00')).replace(tzinfo=None) if date_str else datetime.utcnow()
        except Exception:
            match_dt = datetime.utcnow()

        price = price_tiers[i % len(price_tiers)]

        existing = Match.query.filter_by(home_team_name=home, away_team_name=away).first()
        if not existing:
            match_obj = Match(
                scheduledAt=match_dt,
                home_team_name=home,
                away_team_name=away,
                ticket_price=price,
                status='SCHEDULED',
            )
            db.session.add(match_obj)
            db.session.flush()
            created_matches += 1
        else:
            match_obj = existing

        # Solo crear tickets si no hay suficientes disponibles
        current_avail = Ticket.query.filter_by(matchId=match_obj.matchId, status='Disponible').count()
        to_create = n - current_avail
        for _ in range(max(0, to_create)):
            db.session.add(Ticket(matchId=match_obj.matchId, status='Disponible', price=price))
            created_tickets += 1

    db.session.commit()
    return jsonify({
        "created_matches": created_matches,
        "created_tickets": created_tickets,
        "ttl_minutes": RESERVATION_TTL_MINUTES,
    }), 201
