from flask import Blueprint, request, jsonify
from app.application.services.ticket_service import TicketService
from app.infrastructure.repositories.ticket_repository import SqlAlchemyTicketRepository
from pydantic import ValidationError

ticket_bp = Blueprint('ticket_bp', __name__)

ticket_repo = SqlAlchemyTicketRepository()
ticket_service = TicketService(ticket_repo)

@ticket_bp.route('/tickets', methods=['POST'])
def create_ticket():
    try:
        data = request.get_json()
        result = ticket_service.create_ticket(data)
        return jsonify(result.model_dump()), 201
    except ValidationError as e:
        return jsonify({"error": "Validation Error", "details": e.errors()}), 400
    except ValueError as e:
        return jsonify({"error": "Bad Request", "message": str(e)}), 400

@ticket_bp.route('/tickets/<int:ticket_id>', methods=['GET'])
def get_ticket(ticket_id):
    try:
        result = ticket_service.get_ticket(ticket_id)
        return jsonify(result.model_dump()), 200
    except ValueError as e:
        return jsonify({"error": "Not Found", "message": str(e)}), 404

@ticket_bp.route('/users/<int:user_id>/tickets', methods=['GET'])
def get_user_tickets(user_id):
    results = ticket_service.get_user_tickets(user_id)
    return jsonify([r.model_dump() for r in results]), 200
