"""
AWS Lambda handler — Odds Pre-computation
Trigger: EventBridge every 15 minutes during the tournament.
    rate(15 minutes)

Fetches all upcoming and live World Cup matches, computes dynamic Poisson-based
odds incorporating real market volumes from the sports_bet table, and writes
results to Redis. The Flask API reads from this cache before falling back to
on-demand computation, reducing per-request DB load during peak traffic.

Cache key:  betting:odds:{external_match_id}
Cache TTL:  1200 seconds (20 minutes — longer than the Lambda interval)

Environment variables required:
    DATABASE_URL, SECRET_KEY, JWT_SECRET_KEY, FLASK_ENV=production
    FOOTBALL_API_KEY, FOOTBALL_API_URL
    REDIS_URL
"""
import json
import logging
import os

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

_CACHE_TTL = 1200
_RELEVANT_STATUSES = {"SCHEDULED", "TIMED", "IN_PLAY", "LIVE"}


def handler(event, context):
    os.environ.setdefault("FLASK_ENV", "production")

    from app import create_app
    app = create_app()

    with app.app_context():
        from sqlalchemy import func
        from app.infrastructure.database import db
        from app.domain.models.sports_bet import SportsBet
        from app.infrastructure.external.football_data_service import FootballDataService
        from app.application.services.odds_service import calculate_odds
        from app.infrastructure.cache.redis_client import redis_client

        raw = FootballDataService().get_upcoming_matches()
        matches = [
            m for m in raw.get("matches", [])
            if m.get("status") in _RELEVANT_STATUSES
        ]

        refreshed = 0
        errors = 0

        for m in matches:
            match_id = m.get("id")
            if not match_id:
                continue

            home = (
                m.get("homeTeam", {}).get("shortName")
                or m.get("homeTeam", {}).get("name", "Local")
            )
            away = (
                m.get("awayTeam", {}).get("shortName")
                or m.get("awayTeam", {}).get("name", "Visitante")
            )

            rows = (
                db.session.query(SportsBet.betType, func.sum(SportsBet.stake))
                .filter(SportsBet.matchId == match_id)
                .group_by(SportsBet.betType)
                .all()
            )
            market = {bet_type: float(total) for bet_type, total in rows}

            try:
                odds = calculate_odds(home, away, market_volumes=market)
                redis_client.set(
                    f"betting:odds:{match_id}",
                    json.dumps({"home": home, "away": away, "odds": odds}),
                    ex=_CACHE_TTL,
                )
                refreshed += 1
            except Exception as exc:
                logger.warning({
                    "event": "odds_refresh_failed",
                    "match_id": match_id,
                    "error": str(exc),
                })
                errors += 1

    logger.info({"event": "odds_refresh_complete", "refreshed": refreshed, "errors": errors})

    return {
        "statusCode": 200,
        "body": json.dumps({"refreshed": refreshed, "errors": errors}),
    }
