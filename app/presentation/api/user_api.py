from flask import Blueprint, request, jsonify
from app.application.services.user_service import UserService
from app.infrastructure.repositories.user_repository import SqlAlchemyUserRepository
from pydantic import ValidationError

user_bp = Blueprint('user_bp', __name__)

# Dependencias (Idealmente configuradas a nivel contenedor DI)
user_repo = SqlAlchemyUserRepository()
user_service = UserService(user_repo)

@user_bp.route('/users', methods=['POST'])
def create_user():
    try:
        data = request.get_json()
        result = user_service.create_user(data)
        return jsonify(result.model_dump()), 201
    except ValidationError as e:
        return jsonify({"error": "Validation Error", "details": e.errors()}), 400
    except ValueError as e:
        return jsonify({"error": "Bad Request", "message": str(e)}), 400

@user_bp.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    try:
        result = user_service.get_user(user_id)
        return jsonify(result.model_dump()), 200
    except ValueError as e:
        return jsonify({"error": "Not Found", "message": str(e)}), 404

@user_bp.route('/users', methods=['GET'])
def get_users():
    results = user_service.get_all_users()
    return jsonify([r.model_dump() for r in results]), 200
