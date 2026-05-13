from typing import Optional
from app.domain.models.bet import Bet
from app.domain.models.match import Match

class IBetRepository:
    def get_bet_by_id(self, bet_id: int) -> Optional[Bet]:
        pass

    def get_bet_by_user_match(self, user_id: int, match_id: int) -> Optional[Bet]:
        pass

    def save_bet(self, bet: Bet) -> Bet:
        pass

    def get_match_by_id(self, match_id: int) -> Optional[Match]:
        pass

    def flush(self) -> None:
        pass

    def commit(self) -> None:
        pass

    def rollback(self) -> None:
        pass
