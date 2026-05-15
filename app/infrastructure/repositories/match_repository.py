from typing import Optional, List, Dict, Any
from app.application.interfaces.match_repository import IMatchRepository
from app.domain.models.match import Match
from app.infrastructure.database import db

class SqlAlchemyMatchRepository(IMatchRepository):
    def _to_dict(self, match: Match) -> Dict[str, Any]:
        if not match:
            return None
        return {
            "matchId": match.matchId,
            "status": match.status,
            "scheduledAt": match.scheduledAt.isoformat() if match.scheduledAt else None,
            "stadiumId": match.stadiumId,
            "homeTeamName": match.home_team_name,
            "awayTeamName": match.away_team_name,
            "homeGoals": match.home_goals,
            "awayGoals": match.away_goals,
            "ticketPrice": match.ticket_price,
        }

    def get_by_id(self, match_id: int) -> Optional[Dict[str, Any]]:
        match = Match.query.get(match_id)
        return self._to_dict(match)

    def get_all(self) -> List[Dict[str, Any]]:
        matches = Match.query.all()
        return [self._to_dict(m) for m in matches]

    def get_by_phase(self, phase: str) -> List[Dict[str, Any]]:
        matches = Match.query.filter_by(phase=phase).all()
        return [self._to_dict(m) for m in matches]

    def get_live_matches(self) -> List[Dict[str, Any]]:
        matches = Match.query.filter_by(status='LIVE').all()
        return [self._to_dict(m) for m in matches]

    def save(self, match_data: Dict[str, Any]) -> Dict[str, Any]:
        if "matchId" in match_data and match_data["matchId"]:
            match = Match.query.get(match_data["matchId"])
            for key, value in match_data.items():
                setattr(match, key, value)
        else:
            match = Match(**match_data)
            db.session.add(match)
            
        db.session.commit()
        return self._to_dict(match)
