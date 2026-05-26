import logging
from flask import Blueprint, request, jsonify
from app.application.services.match_service import MatchService

_log = logging.getLogger(__name__)
from app.infrastructure.repositories.match_repository import SqlAlchemyMatchRepository
from app.infrastructure.database import db
from app.domain.models.match import Match
from app.domain.models.bet import Bet
from app.infrastructure.external.notification_service import notification_service
from app.infrastructure.external.geocoding_service import geocode_stadium, geocode_city
from pydantic import ValidationError

match_bp = Blueprint('match_bp', __name__)


def _calculate_bet_points(bet, match) -> int:
    if bet.home_goals == match.home_goals and bet.away_goals == match.away_goals:
        return 3
    actual = (match.home_goals > match.away_goals) - (match.home_goals < match.away_goals)
    pred = (bet.home_goals > bet.away_goals) - (bet.home_goals < bet.away_goals)
    return 1 if actual == pred else 0


def _notify_bet_result(entry: dict, match, home: str, away: str) -> None:
    if entry["points"] > 0:
        msg = (
            f"¡Acertaste {entry['points']} punto(s) en {home} vs {away} "
            f"({match.home_goals}-{match.away_goals})!"
        )
    else:
        msg = f"No acertaste el resultado de {home} vs {away} ({match.home_goals}-{match.away_goals})."
    try:
        notification_service.notify_user_from_id(
            user_id=entry["user_id"],
            title="Resultado del partido",
            body=msg,
            notif_type="match_result",
            reference_id=match.matchId,
            reference_type="match",
        )
    except Exception as _e:
        _log.debug({"event": "match_result_notification_failed", "details": str(_e)})

match_repo = SqlAlchemyMatchRepository()
match_service = MatchService(match_repo)


def _match_to_dict(match: Match) -> dict:
    from app.domain.models.phase import Phase
    phases = [p.phaseName for p in Phase.query.filter_by(matchId=match.matchId).all()]
    return {
        "matchId":      match.matchId,
        "status":       match.status,
        "scheduledAt":  match.scheduledAt.isoformat() if match.scheduledAt else None,
        "stadiumId":    match.stadiumId,
        "stadiumName":  match.stadium.name if match.stadium else None,
        "city":         match.stadium.city.name if match.stadium and match.stadium.city else None,
        "homeTeamName": match.home_team_name,
        "awayTeamName": match.away_team_name,
        "homeGoals":    match.home_goals,
        "awayGoals":    match.away_goals,
        "ticketPrice":  match.ticket_price,
        "phases":       phases,
    }


@match_bp.route('/matches', methods=['POST'])
def create_match():
    try:
        data = request.get_json()
        result = match_service.create_match(data)
        return jsonify(result.model_dump()), 201
    except ValidationError as e:
        return jsonify({"error": "Validation Error", "details": e.errors()}), 400
    except ValueError as e:
        return jsonify({"error": "Bad Request", "message": str(e)}), 400

@match_bp.route('/matches/<int:match_id>', methods=['GET'])
def get_match(match_id):
    try:
        result = match_service.get_match(match_id)
        return jsonify(result.model_dump()), 200
    except ValueError as e:
        return jsonify({"error": "Not Found", "message": str(e)}), 404

@match_bp.route('/matches', methods=['GET'])
def get_matches():
    phase_filter = request.args.get('phase', '').strip()
    if phase_filter:
        from app.domain.models.phase import Phase
        phase_match_ids = db.session.query(Phase.matchId).filter(
            db.func.lower(Phase.phaseName).contains(phase_filter.lower())
        ).all()
        ids = [p[0] for p in phase_match_ids]
        matches = Match.query.filter(Match.matchId.in_(ids)).all()
        return jsonify([_match_to_dict(m) for m in matches]), 200
    results = match_service.get_all_matches()
    return jsonify([r.model_dump() for r in results]), 200

@match_bp.route('/matches/live', methods=['GET'])
def get_live_matches():
    results = match_service.get_live_matches()
    return jsonify([r.model_dump() for r in results]), 200


@match_bp.route('/matches/agenda', methods=['GET'])
def get_agenda():
    """
    Returns upcoming matches filtered by optional city or stadium.
    Query params: city, stadium, phase
    """
    city_name    = request.args.get('city', '').strip()
    stadium_name = request.args.get('stadium', '').strip()
    phase_name   = request.args.get('phase', '').strip()

    from app.domain.models.phase import Phase
    from app.domain.models.stadium import Stadium
    from app.domain.models.city import City

    query = Match.query.filter(Match.status.in_(['SCHEDULED', 'LIVE']))

    if stadium_name:
        stadium = Stadium.query.filter(
            db.func.lower(Stadium.name).contains(stadium_name.lower())
        ).first()
        if stadium:
            query = query.filter(Match.stadiumId == stadium.stadiumId)
        else:
            return jsonify([]), 200

    elif city_name:
        city = City.query.filter(
            db.func.lower(City.name).contains(city_name.lower())
        ).first()
        if city:
            stadium_ids = [s.stadiumId for s in Stadium.query.filter_by(cityId=city.cityId).all()]
            query = query.filter(Match.stadiumId.in_(stadium_ids))
        else:
            return jsonify([]), 200

    if phase_name:
        phase_match_ids = db.session.query(Phase.matchId).filter(
            db.func.lower(Phase.phaseName).contains(phase_name.lower())
        ).all()
        ids = [p[0] for p in phase_match_ids]
        query = query.filter(Match.matchId.in_(ids))

    matches = query.order_by(Match.scheduledAt.asc()).all()
    return jsonify([_match_to_dict(m) for m in matches]), 200


@match_bp.route('/matches/phases', methods=['GET'])
def get_matches_by_phase():
    """List all available phases with their match counts."""
    from app.domain.models.phase import Phase
    rows = db.session.query(
        Phase.phaseName, db.func.count(Phase.idPhase)
    ).group_by(Phase.phaseName).all()
    return jsonify([{"phase": r[0], "match_count": r[1]} for r in rows]), 200


@match_bp.route('/stadiums', methods=['GET'])
def get_stadiums():
    """Returns all stadiums with city info and geocoded coordinates."""
    from app.domain.models.stadium import Stadium
    from app.domain.models.city import City

    stadiums = Stadium.query.all()
    result = []
    for s in stadiums:
        city_name = s.city.name if s.city else None
        geo = geocode_stadium(s.name, city_name)
        entry = {
            "stadiumId":  s.stadiumId,
            "name":       s.name,
            "capacity":   s.capacity,
            "cityId":     s.cityId,
            "city":       city_name,
            "lat":        geo["lat"] if geo else None,
            "lon":        geo["lon"] if geo else None,
        }
        result.append(entry)
    return jsonify(result), 200


@match_bp.route('/cities', methods=['GET'])
def get_cities():
    """Returns all host cities with geocoded coordinates."""
    from app.domain.models.city import City
    cities = City.query.all()
    result = []
    for c in cities:
        geo = geocode_city(c.name)
        result.append({
            "cityId": c.cityId,
            "name":   c.name,
            "lat":    geo["lat"] if geo else None,
            "lon":    geo["lon"] if geo else None,
        })
    return jsonify(result), 200


@match_bp.route('/matches/<int:match_id>/finalize', methods=['POST'])
def finalize_match(match_id):
    """
    Admin endpoint: sets final score, marks match FINISHED, scores all
    prediction bets (3 pts exact score, 1 pt correct outcome) and sends
    notifications to each affected user.

    Body: { "home_goals": int, "away_goals": int }
    """
    data = request.get_json() or {}
    home_goals = data.get('home_goals')
    away_goals = data.get('away_goals')

    if home_goals is None or away_goals is None:
        return jsonify({"error": "home_goals and away_goals are required"}), 400

    match = Match.query.get(match_id)
    if not match:
        return jsonify({"error": "Match not found"}), 404

    if match.status == 'FINISHED':
        return jsonify({"error": "Match already finalized"}), 409

    match.home_goals = int(home_goals)
    match.away_goals = int(away_goals)
    match.status = 'FINISHED'

    bets = Bet.query.filter_by(match_id=match_id).all()
    scored = [
        {"user_id": bet.user_id, "bet_id": bet.bet_id, "points": _calculate_bet_points(bet, match)}
        for bet in bets
    ]

    try:
        db.session.commit()
    except Exception as exc:
        db.session.rollback()
        return jsonify({"error": "DB error", "details": str(exc)}), 500

    home = match.home_team_name or "Local"
    away = match.away_team_name or "Visitante"
    for entry in scored:
        _notify_bet_result(entry, match, home, away)

    return jsonify({
        "match_id": match_id,
        "home_goals": match.home_goals,
        "away_goals": match.away_goals,
        "status": "FINISHED",
        "bets_scored": len(scored),
        "scored": scored,
    }), 200
