from typing import Optional
from app.domain.models.bet import Bet
from app.domain.models.match import Match

class IBetRepository:
    def get_bet_by_id(self, bet_id: int) -> Optional[Bet]:
        raise NotImplementedError

    def get_bet_by_user_match(self, user_id: int, match_id: int) -> Optional[Bet]:
        raise NotImplementedError

    def save_bet(self, bet: Bet) -> Bet:
        raise NotImplementedError

    def get_match_by_id(self, match_id: int) -> Optional[Match]:
        raise NotImplementedError

    def flush(self) -> None:
        raise NotImplementedError

    def commit(self) -> None:
        raise NotImplementedError

    def rollback(self) -> None:
        raise NotImplementedError
