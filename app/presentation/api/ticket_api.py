from flask import Blueprint, request, jsonify
from app.application.services.ticket_service import TicketService
from app.infrastructure.repositories.ticket_repository import SqlAlchemyTicketRepository
from app.presentation.middlewares.auth import require_role
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
        return jsonify(result.model_dump()), 200
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
    """Reservada → Expirada para todas las reservas con TTL vencido."""
    result = ticket_service.expire_reservations()
    return jsonify(result), 200
