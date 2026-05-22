from flask import Blueprint, request, jsonify
from app.application.services.feed_service import feed_service

feed_bp = Blueprint('feed_bp', __name__)

_ERR_USER_ID_REQUIRED = "userId requerido"


def _viewer() -> int:
    """Extrae user_id del header o query param. Devuelve 0 si anónimo."""
    uid = request.args.get('viewer_id') or request.json.get('userId', 0) if request.is_json else 0
    try:
        return int(uid)
    except (TypeError, ValueError):
        return 0


# ── Posts ─────────────────────────────────────────────────────────────────────

@feed_bp.route('/feed', methods=['GET'])
def get_feed():
    viewer_id = int(request.args.get('viewer_id', 0))
    page      = int(request.args.get('page', 1))
    group_id  = request.args.get('group_id', type=int)
    posts     = feed_service.get_feed(viewer_id, page, group_id=group_id)
    return jsonify(posts), 200


@feed_bp.route('/feed', methods=['POST'])
def create_post():
    data     = request.get_json() or {}
    user_id  = data.get('userId')
    content  = data.get('content', '')
    images   = data.get('images', [])
    group_id = data.get('groupId')
    if not user_id:
        return jsonify({"error": _ERR_USER_ID_REQUIRED}), 400
    try:
        post = feed_service.create_post(int(user_id), content, images,
                                        group_id=int(group_id) if group_id else None)
        return jsonify(post), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


@feed_bp.route('/feed/<int:post_id>', methods=['PATCH'])
def edit_post(post_id):
    data    = request.get_json() or {}
    user_id = data.get('userId')
    content = data.get('content', '')
    if not user_id:
        return jsonify({"error": _ERR_USER_ID_REQUIRED}), 400
    try:
        post = feed_service.edit_post(post_id, int(user_id), content)
        return jsonify(post), 200
    except (ValueError, PermissionError) as e:
        return jsonify({"error": str(e)}), 403


@feed_bp.route('/feed/<int:post_id>', methods=['DELETE'])
def delete_post(post_id):
    data    = request.get_json() or {}
    user_id = data.get('userId')
    if not user_id:
        return jsonify({"error": _ERR_USER_ID_REQUIRED}), 400
    try:
        feed_service.delete_post(post_id, int(user_id))
        return jsonify({"ok": True}), 200
    except (ValueError, PermissionError) as e:
        return jsonify({"error": str(e)}), 403


@feed_bp.route('/feed/<int:post_id>/like', methods=['POST'])
def toggle_like(post_id):
    data    = request.get_json() or {}
    user_id = data.get('userId')
    if not user_id:
        return jsonify({"error": _ERR_USER_ID_REQUIRED}), 400
    try:
        result = feed_service.toggle_like(post_id, int(user_id))
        return jsonify(result), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 404


# ── Comments ──────────────────────────────────────────────────────────────────

@feed_bp.route('/feed/<int:post_id>/comments', methods=['GET'])
def get_comments(post_id):
    viewer_id = int(request.args.get('viewer_id', 0))
    comments  = feed_service.get_comments(post_id, viewer_id)
    return jsonify(comments), 200


@feed_bp.route('/feed/<int:post_id>/comments', methods=['POST'])
def add_comment(post_id):
    data      = request.get_json() or {}
    user_id   = data.get('userId')
    content   = data.get('content', '')
    parent_id = data.get('parentId')
    if not user_id:
        return jsonify({"error": _ERR_USER_ID_REQUIRED}), 400
    try:
        comment = feed_service.add_comment(post_id, int(user_id), content,
                                           int(parent_id) if parent_id else None)
        return jsonify(comment), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


@feed_bp.route('/feed/comments/<int:comment_id>', methods=['DELETE'])
def delete_comment(comment_id):
    data    = request.get_json() or {}
    user_id = data.get('userId')
    if not user_id:
        return jsonify({"error": _ERR_USER_ID_REQUIRED}), 400
    try:
        feed_service.delete_comment(comment_id, int(user_id))
        return jsonify({"ok": True}), 200
    except (ValueError, PermissionError) as e:
        return jsonify({"error": str(e)}), 403


@feed_bp.route('/feed/comments/<int:comment_id>/like', methods=['POST'])
def toggle_comment_like(comment_id):
    data    = request.get_json() or {}
    user_id = data.get('userId')
    if not user_id:
        return jsonify({"error": _ERR_USER_ID_REQUIRED}), 400
    try:
        result = feed_service.toggle_comment_like(comment_id, int(user_id))
        return jsonify(result), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
