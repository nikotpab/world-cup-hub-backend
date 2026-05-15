from flask import Blueprint, jsonify
from app.infrastructure.external.news_service import news_service

news_bp = Blueprint('news_bp', __name__)


@news_bp.route('/news', methods=['GET'])
def get_news():
    """Devuelve noticias del Mundial 2026 desde NewsAPI (cacheadas 15 min)."""
    articles = news_service.get_wc2026_news()
    return jsonify({"articles": articles, "count": len(articles)}), 200
