import requests
from flask import Blueprint, request, Response, jsonify

proxy_bp = Blueprint('proxy_bp', __name__)

@proxy_bp.route('/proxy/image', methods=['GET'])
def proxy_image():
    """Proxies an image request to bypass browser CORS restrictions."""
    url = request.args.get('url')
    if not url:
        return jsonify({"error": "Missing URL"}), 400
    
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        
        return Response(
            resp.content,
            mimetype=resp.headers.get('Content-Type', 'image/svg+xml'),
            status=200
        )
    except Exception as e:
        return jsonify({"error": "Failed to fetch image", "details": str(e)}), 500