from flask import Blueprint, request, jsonify
from datetime import datetime, timezone
from app.infrastructure.database import db
from app.domain.models.sports_bet import SportsBet
from app.domain.models.album import Album
from app.application.services.odds_service import calculate_odds
from app.infrastructure.external.football_data_service import FootballDataService
from app.infrastructure.logger import app_logger

sports_bet_bp = Blueprint("sports_bet_bp", __name__)
_football_svc = FootballDataService()


def _enrich_match(m: dict) -> dict:
    """Agrega cuotas Poisson a un partido de la API."""
    home = m.get("homeTeam", {}).get("shortName") or m.get("homeTeam", {}).get("name", "Local")
    away = m.get("awayTeam", {}).get("shortName") or m.get("awayTeam", {}).get("name", "Visitante")
    try:
        odds = calculate_odds(home, away)
    except Exception:
        odds = {"home_win": 2.0, "draw": 3.2, "away_win": 3.5,
                "prob_home": 45.0, "prob_draw": 28.0, "prob_away": 27.0,
                "expected_goals": {"home": 1.35, "away": 1.10},
                "top_scores": []}
    return {
        "match_id":  m.get("id"),
        "home_name": home,
        "away_name": away,
        "date":      m.get("utcDate"),
        "status":    m.get("status"),
        "score": {
            "home": (m.get("score") or {}).get("fullTime", {}).get("home"),
            "away": (m.get("score") or {}).get("fullTime", {}).get("away"),
        },
        "odds": odds,
    }


@sports_bet_bp.route("/matches/betting", methods=["GET"])
def get_betting_matches():
    """Devuelve próximos partidos del Mundial con cuotas calculadas."""
    raw = _football_svc.get_upcoming_matches()
    matches = raw.get("matches", [])

    # Filtrar solo partidos programados o en juego
    relevant = [m for m in matches if m.get("status") in ("SCHEDULED", "TIMED", "IN_PLAY", "LIVE")][:20]

    if not relevant:
        # Fallback con datos mock enriquecidos
        relevant = raw.get("matches", [])[:10]

    result = [_enrich_match(m) for m in relevant]
    return jsonify({"matches": result, "count": len(result)}), 200


@sports_bet_bp.route("/matches/<int:match_id>/odds", methods=["GET"])
def get_match_odds(match_id: int):
    """Calcula cuotas para un partido específico dado los nombres de los equipos."""
    home = request.args.get("home", "")
    away = request.args.get("away", "")
    if not home or not away:
        return jsonify({"error": "ERR_BAD_REQUEST", "message": "home y away son requeridos"}), 400
    odds = calculate_odds(home, away)
    return jsonify({"match_id": match_id, "home": home, "away": away, "odds": odds}), 200


@sports_bet_bp.route("/sports-bets", methods=["POST"])
def place_bet():
    """
    Registra una apuesta deportiva descontando monedas del álbum.
    Body: { userId, matchId, homeName, awayName, betType, betLabel, odds, stake }
    """
    data = request.get_json() or {}
    required = ("userId", "matchId", "homeName", "awayName", "betType", "betLabel", "odds", "stake")
    missing = [f for f in required if f not in data]
    if missing:
        return jsonify({"error": "ERR_VALIDATION", "missing": missing}), 400

    user_id  = int(data["userId"])
    stake    = int(data["stake"])
    odds_val = float(data["odds"])

    if stake <= 0:
        return jsonify({"error": "ERR_BAD_REQUEST", "message": "El monto debe ser mayor a 0"}), 400
    if odds_val < 1.01:
        return jsonify({"error": "ERR_BAD_REQUEST", "message": "Cuota inválida"}), 400

    # Verificar y descontar coins del álbum
    album = Album.query.filter_by(idUser=user_id).first()
    if not album:
        album = Album(idUser=user_id, packBalance=0, coins=0)
        db.session.add(album)
    if (album.coins or 0) < stake:
        return jsonify({"error": "ERR_INSUFFICIENT_FUNDS",
                        "message": f"Saldo insuficiente. Tienes {album.coins} monedas."}), 400

    potential = int(stake * odds_val)
    album.coins -= stake

    bet = SportsBet(
        userId=user_id,
        matchId=int(data["matchId"]),
        homeName=data["homeName"],
        awayName=data["awayName"],
        betType=data["betType"],
        betLabel=data["betLabel"],
        odds=odds_val,
        stake=stake,
        potentialWin=potential,
        status="pending",
        createdAt=datetime.now(timezone.utc),
    )
    db.session.add(bet)
    db.session.commit()

    app_logger.info({"event": "sports_bet_placed", "bet_id": bet.id,
                     "user_id": user_id, "stake": stake, "odds": odds_val, "audit": True})

    return jsonify({
        "success":       True,
        "bet_id":        bet.id,
        "bet_label":     bet.betLabel,
        "odds":          bet.odds,
        "stake":         bet.stake,
        "potential_win": bet.potentialWin,
        "coins_balance": album.coins,
    }), 201


@sports_bet_bp.route("/users/<int:user_id>/sports-bets", methods=["GET"])
def get_user_bets(user_id: int):
    bets = SportsBet.query.filter_by(userId=user_id).order_by(SportsBet.createdAt.desc()).limit(50).all()
    return jsonify([{
        "id":           b.id,
        "match_id":     b.matchId,
        "home_name":    b.homeName,
        "away_name":    b.awayName,
        "bet_type":     b.betType,
        "bet_label":    b.betLabel,
        "odds":         b.odds,
        "stake":        b.stake,
        "potential_win":b.potentialWin,
        "status":       b.status,
        "created_at":   b.createdAt.isoformat() if b.createdAt else None,
    } for b in bets]), 200
