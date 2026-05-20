"""
AWS Lambda handler — Match and Ticket Seeding
Trigger: EventBridge daily at 06:00 UTC during the pre-tournament seeding window.
    cron(0 6 * * ? *)

Pulls upcoming World Cup matches from football-data.org and creates Match + Ticket
records in the database. Idempotent: existing matches and tickets are not duplicated.

Event payload (optional):
    { "tickets_per_match": 30, "max_matches": 15 }

Environment variables required:
    DATABASE_URL, SECRET_KEY, JWT_SECRET_KEY, FLASK_ENV=production
    FOOTBALL_API_KEY, FOOTBALL_API_URL
"""
import json
import logging
import os
from datetime import datetime, timezone

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

_PRICE_TIERS = [120.0, 150.0, 200.0, 280.0, 350.0]


def _parse_dt(date_str: str):
    try:
        return datetime.fromisoformat(
            date_str.replace("Z", "+00:00")
        ).replace(tzinfo=None) if date_str else datetime.now(timezone.utc).replace(tzinfo=None)
    except Exception:
        return datetime.now(timezone.utc).replace(tzinfo=None)


def _ensure_match(db, Match, home, away, match_dt, price):
    existing = Match.query.filter_by(home_team_name=home, away_team_name=away).first()
    if existing:
        return existing, 0
    match_obj = Match(
        scheduledAt=match_dt,
        home_team_name=home,
        away_team_name=away,
        ticket_price=price,
        status="SCHEDULED",
    )
    db.session.add(match_obj)
    db.session.flush()
    return match_obj, 1


def handler(event, context):
    os.environ.setdefault("FLASK_ENV", "production")

    body = event if isinstance(event, dict) else {}
    tickets_per_match = int(body.get("tickets_per_match", 30))
    max_matches = int(body.get("max_matches", 15))

    from app import create_app
    app = create_app()

    with app.app_context():
        from app.infrastructure.database import db
        from app.domain.models.match import Match
        from app.domain.models.ticket import Ticket
        from app.infrastructure.external.football_data_service import FootballDataService

        matches_data = FootballDataService().get_upcoming_matches().get("matches", [])[:max_matches]

        created_matches = 0
        created_tickets = 0

        for i, m in enumerate(matches_data):
            home = (
                (m.get("homeTeam") or {}).get("shortName")
                or (m.get("homeTeam") or {}).get("name", "Local")
            )
            away = (
                (m.get("awayTeam") or {}).get("shortName")
                or (m.get("awayTeam") or {}).get("name", "Visitante")
            )
            price = _PRICE_TIERS[i % len(_PRICE_TIERS)]
            match_obj, new_match = _ensure_match(
                db, Match, home, away, _parse_dt(m.get("utcDate")), price
            )
            created_matches += new_match

            existing_count = Ticket.query.filter_by(
                matchId=match_obj.matchId, status="Disponible"
            ).count()
            to_create = max(0, tickets_per_match - existing_count)
            for _ in range(to_create):
                db.session.add(Ticket(matchId=match_obj.matchId, status="Disponible", price=price))
                created_tickets += 1

        db.session.commit()

    logger.info({
        "event": "matches_seeded",
        "created_matches": created_matches,
        "created_tickets": created_tickets,
        "tickets_per_match": tickets_per_match,
    })

    return {
        "statusCode": 200,
        "body": json.dumps({
            "created_matches": created_matches,
            "created_tickets": created_tickets,
        }),
    }
