from flask import Blueprint, request, jsonify
from datetime import datetime, timezone
from sqlalchemy import func
from app.infrastructure.database import db
from app.domain.models.sports_bet import SportsBet
from app.domain.models.album import Album
from app.application.services.odds_service import calculate_odds
from app.infrastructure.external.football_data_service import FootballDataService
from app.infrastructure.logger import app_logger

sports_bet_bp = Blueprint("sports_bet_bp", __name__)
_football_svc = FootballDataService()


def _get_market_volumes(match_id: int) -> dict:
    """Obtiene el volumen total de apuestas por cada resultado para un partido."""
    try:
        results = db.session.query(
            SportsBet.betType, 
            func.sum(SportsBet.stake)
        ).filter(SportsBet.matchId == match_id).group_by(SportsBet.betType).all()
        return {bet_type: float(total) for bet_type, total in results}
    except Exception:
        return {}


def _enrich_match(m: dict) -> dict:
    """Agrega cuotas Poisson dinámicas a un partido de la API."""
    match_id = m.get("id")
    home = m.get("homeTeam", {}).get("shortName") or m.get("homeTeam", {}).get("name", "Local")
    away = m.get("awayTeam", {}).get("shortName") or m.get("awayTeam", {}).get("name", "Visitante")
    
    # Obtener volúmenes del mercado (apuestas de usuarios reales)
    market = _get_market_volumes(match_id) if match_id else {}
    
    try:
        odds = calculate_odds(home, away, market_volumes=market)
    except Exception:
        odds = {"home_win": 2.0, "draw": 3.2, "away_win": 3.5,
                "prob_home": 45.0, "prob_draw": 28.0, "prob_away": 27.0,
                "expected_goals": {"home": 1.35, "away": 1.10},
                "top_scores": []}
    return {
        "match_id":  match_id,
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
    """Devuelve próximos partidos del Mundial con cuotas dinámicas."""
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
    """Calcula cuotas dinámicas para un partido específico."""
    home = request.args.get("home", "")
    away = request.args.get("away", "")
    if not home or not away:
        return jsonify({"error": "ERR_BAD_REQUEST", "message": "home y away son requeridos"}), 400
        
    market = _get_market_volumes(match_id)
    odds = calculate_odds(home, away, market_volumes=market)
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

    # Pago con Stripe test mode
    from app.infrastructure.external.payment_service import StripePaymentService
    amount_cents = stake * 100  # stake en USD
    try:
        payment = StripePaymentService().create_and_confirm_payment(
            amount_cents=amount_cents,
            metadata={"user_id": user_id, "bet_type": data["betType"],
                      "match_id": data["matchId"]},
        )
    except ValueError as e:
        return jsonify({"error": "ERR_PAYMENT_FAILED", "message": str(e)}), 402

    potential = int(stake * odds_val)

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
    setattr(bet, 'stripe_intent_id', payment["intent_id"])
    db.session.add(bet)
    db.session.commit()

    app_logger.info({"event": "sports_bet_placed", "bet_id": bet.id,
                     "user_id": user_id, "stake": stake, "odds": odds_val, "audit": True})

    return jsonify({
        "success":         True,
        "bet_id":          bet.id,
        "bet_label":       bet.betLabel,
        "odds":            bet.odds,
        "stake":           bet.stake,
        "potential_win":   bet.potentialWin,
        "stripe_intent_id": payment["intent_id"],
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
