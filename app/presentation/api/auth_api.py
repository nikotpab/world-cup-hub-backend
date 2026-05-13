from flask import Blueprint, request, jsonify
from app.application.services.auth_service import AuthService
from app.infrastructure.repositories.user_repository import SqlAlchemyUserRepository

auth_bp = Blueprint('auth_bp', __name__)

user_repo = SqlAlchemyUserRepository()
auth_service = AuthService(user_repo)

@auth_bp.route('/auth/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        result = auth_service.login(data)
        return jsonify(result), 200
    except ValueError as e:
        return jsonify({"error": "Unauthorized", "message": str(e)}), 401
