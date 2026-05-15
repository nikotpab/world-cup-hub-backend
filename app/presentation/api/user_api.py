from flask import Blueprint, request, jsonify
from app.application.services.user_service import UserService
from app.infrastructure.repositories.user_repository import SqlAlchemyUserRepository
from app.infrastructure.database import db
from app.domain.models.user import User
from pydantic import ValidationError

user_bp = Blueprint('user_bp', __name__)

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


@user_bp.route('/users/<int:user_id>/profile-picture', methods=['PUT'])
def update_profile_picture(user_id):
    """Updates the profile picture for a user."""
    data = request.get_json() or {}
    picture = data.get('profilePicture', '')

    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    user.profilePicture = picture
    try:
        db.session.commit()
    except Exception as exc:
        db.session.rollback()
        return jsonify({"error": "DB error", "details": str(exc)}), 500

    return jsonify({"ok": True, "user_id": user_id, "profilePicture": user.profilePicture}), 200

@user_bp.route('/users/<int:user_id>/fcm-token', methods=['POST'])
def update_fcm_token(user_id):
    data = request.get_json() or {}
    token = data.get('token', '').strip()
    if not token:
        return jsonify({"error": "token is required"}), 400

    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    user.fcmToken = token
    try:
        db.session.commit()
    except Exception as exc:
        db.session.rollback()
        return jsonify({"error": "DB error", "details": str(exc)}), 500

    return jsonify({"ok": True, "user_id": user_id}), 200
