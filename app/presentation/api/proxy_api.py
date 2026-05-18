import os
import re
import requests
from urllib.parse import urlparse
from flask import Blueprint, request, Response, jsonify

proxy_bp = Blueprint('proxy_bp', __name__)

_ALLOWED_HOSTS = frozenset(
    h.strip()
    for h in os.environ.get(
        'PROXY_ALLOWED_HOSTS',
        'crests.football-data.org,media.api-sports.io,upload.wikimedia.org,img.mlbstatic.com,newsapi.org'
    ).split(',')
    if h.strip()
)

_SAFE_PATH_RE = re.compile(r'^/[a-zA-Z0-9/_\-\.%]*$')


@proxy_bp.route('/proxy/image', methods=['GET'])
def proxy_image():
    """Proxies image requests to bypass browser CORS restrictions.
    Only hosts listed in PROXY_ALLOWED_HOSTS are permitted.
    """
    url = request.args.get('url')
    if not url:
        return jsonify({"error": "Missing URL"}), 400

    parsed = urlparse(url)
    if parsed.scheme not in ('http', 'https'):
        return jsonify({"error": "URL not allowed"}), 400

    if parsed.netloc not in _ALLOWED_HOSTS:
        return jsonify({"error": "URL not allowed"}), 400

    if not _SAFE_PATH_RE.match(parsed.path or '/'):
        return jsonify({"error": "URL not allowed"}), 400

    safe_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
    if parsed.query:
        safe_url += f"?{parsed.query}"

    try:
        resp = requests.get(safe_url, timeout=10)
        resp.raise_for_status()
        return Response(
            resp.content,
            mimetype=resp.headers.get('Content-Type', 'image/svg+xml'),
            status=200
        )
    except Exception as e:
        return jsonify({"error": "Failed to fetch image", "details": str(e)}), 500
