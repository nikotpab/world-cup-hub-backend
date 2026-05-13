from typing import Optional
from app.application.interfaces.bet_repository import IBetRepository
from app.domain.models.bet import Bet
from app.domain.models.match import Match
from app.infrastructure.database import db

class SqlAlchemyBetRepository(IBetRepository):
    def get_bet_by_id(self, bet_id: int) -> Optional[Bet]:
        return Bet.query.get(bet_id)

    def get_bet_by_user_match(self, user_id: int, match_id: int) -> Optional[Bet]:
        return Bet.query.filter_by(user_id=user_id, match_id=match_id).first()

    def save_bet(self, bet: Bet) -> Bet:
        db.session.add(bet)
        return bet

    def get_match_by_id(self, match_id: int) -> Optional[Match]:
        return Match.query.get(match_id)

    def flush(self) -> None:
        db.session.flush()

    def commit(self) -> None:
        db.session.commit()

    def rollback(self) -> None:
        db.session.rollback()
