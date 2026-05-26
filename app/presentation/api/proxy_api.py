import os
import re
import requests
import socket
from ipaddress import ip_address
from urllib.parse import urlparse
from flask import Blueprint, request, Response, jsonify

proxy_bp = Blueprint('proxy_bp', __name__)

_ERR_URL_NOT_ALLOWED = "URL not allowed"

_ALLOWED_HOSTS = frozenset(
    h.strip()
    for h in os.environ.get(
        'PROXY_ALLOWED_HOSTS',
        'crests.football-data.org,media.api-sports.io,upload.wikimedia.org,img.mlbstatic.com,newsapi.org'
    ).split(',')
    if h.strip()
)

def _is_safe_public_host(host):
    # Remove port if present
    host_clean = host.split(':')[0]
    try:
        addrinfo = socket.getaddrinfo(host_clean, None)
        for item in addrinfo:
            ip_str = item[4][0]
            if ip_str.startswith('[') and ip_str.endswith(']'):
                ip_str = ip_str[1:-1]
            addr = ip_address(ip_str)
            if addr.is_private or addr.is_loopback or addr.is_link_local:
                return False
        return True
    except Exception:
        return False


@proxy_bp.route('/proxy/image', methods=['GET'])
def proxy_image():
    """Proxies image requests to bypass browser CORS restrictions.
    Only hosts listed in PROXY_ALLOWED_HOSTS are permitted, or hosts
    resolving to safe public IP addresses.
    """
    url = request.args.get('url')
    if not url:
        return jsonify({"error": "Missing URL"}), 400

    parsed = urlparse(url)
    if parsed.scheme not in ('http', 'https'):
        return jsonify({"error": _ERR_URL_NOT_ALLOWED}), 400

    # Allow if in whitelist OR resolves to a safe public IP
    if parsed.netloc not in _ALLOWED_HOSTS:
        if not _is_safe_public_host(parsed.netloc):
            return jsonify({"error": _ERR_URL_NOT_ALLOWED}), 400

    if '..' in (parsed.path or ''):
        return jsonify({"error": _ERR_URL_NOT_ALLOWED}), 400

    safe_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
    if parsed.query:
        safe_url += f"?{parsed.query}"

    try:
        resp = requests.get(safe_url, timeout=10)
        resp.raise_for_status()
        return Response(
            resp.content,
            mimetype=resp.headers.get('Content-Type', 'image/jpeg'),
            status=200
        )
    except Exception as e:
        return jsonify({"error": "Failed to fetch image", "details": str(e)}), 500
