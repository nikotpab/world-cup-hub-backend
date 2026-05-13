from typing import Optional, List, Dict, Any
from app.application.interfaces.community_repository import ICommunityRepository
from app.domain.models.community import Community
from app.domain.models.user import User
from app.domain.models.match import Match
from app.domain.models.bet import Bet
from app.infrastructure.database import db

class SqlAlchemyCommunityRepository(ICommunityRepository):
    def get_community_by_id(self, community_id: int) -> Optional[Community]:
        return Community.query.get(community_id)

    def get_community_by_code(self, code: int) -> Optional[Community]:
        return Community.query.filter_by(invitation_code=code).first()

    def save_community(self, community: Community) -> Community:
        db.session.add(community)
        return community

    def get_user_by_id(self, user_id: int) -> Optional[User]:
        return User.query.get(user_id)

    def get_community_ranking(self, community_id: int) -> List[Dict[str, Any]]:
        # Obtener los usuarios de la comunidad
        community = self.get_community_by_id(community_id)
        if not community:
            return []
            
        user_ids = [user.user_id for user in community.users]
        if not user_ids:
            return []

        # Obtener todas las apuestas de los usuarios en partidos finalizados
        bets_and_matches = db.session.query(Bet, Match).join(Match).filter(
            Bet.user_id.in_(user_ids),
            Match.status == 'FINISHED'
        ).all()
        
        user_scores = {uid: 0 for uid in user_ids}
        for bet, match in bets_and_matches:
            points = 0
            if bet.home_goals == match.homeGoals and bet.away_goals == match.awayGoals:
                points = 3
            else:
                # Verificar si acertó ganador/empate
                actual_res = (match.homeGoals > match.awayGoals) - (match.homeGoals < match.awayGoals)
                pred_res = (bet.home_goals > bet.away_goals) - (bet.home_goals < bet.away_goals)
                if actual_res == pred_res:
                    points = 1
            
            user_scores[bet.user_id] += points
            
        ranking = []
        for user_id, total_points in user_scores.items():
            user = User.query.get(user_id)
            ranking.append({
                "userId": user_id,
                "name": f"{user.firstName} {user.lastName}",
                "points": total_points
            })
            
        return sorted(ranking, key=lambda x: x['points'], reverse=True)

    def commit(self) -> None:
        db.session.commit()

    def rollback(self) -> None:
        db.session.rollback()
