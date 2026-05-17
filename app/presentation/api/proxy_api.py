import os
import requests
from urllib.parse import urlparse
from flask import Blueprint, request, Response, jsonify

proxy_bp = Blueprint('proxy_bp', __name__)

_ALLOWED_HOSTS = frozenset(
    h.strip()
    for h in os.environ.get(
        'PROXY_ALLOWED_HOSTS',
        'crests.football-data.org,media.api-sports.io,upload.wikimedia.org,img.mlbstatic.com'
    ).split(',')
    if h.strip()
)


@proxy_bp.route('/proxy/image', methods=['GET'])
def proxy_image():
    """Proxies an image request to bypass browser CORS restrictions."""
    url = request.args.get('url')
    if not url:
        return jsonify({"error": "Missing URL"}), 400

    parsed = urlparse(url)
    if parsed.scheme not in ('http', 'https') or parsed.hostname not in _ALLOWED_HOSTS:
        return jsonify({"error": "URL not allowed"}), 400

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
