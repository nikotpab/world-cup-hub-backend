from typing import Optional, List, Dict, Any
from app.application.interfaces.trade_repository import ITradeRepository
from app.domain.models.trade_proposal import TradeProposal
from app.infrastructure.database import db
from sqlalchemy.exc import SQLAlchemyError

class SqlAlchemyTradeRepository(ITradeRepository):
    def get_by_id(self, trade_id: int) -> Optional[TradeProposal]:
        return TradeProposal.query.get(trade_id)

    def save(self, trade: TradeProposal) -> TradeProposal:
        db.session.add(trade)
        db.session.flush() # Sync with DB but don't commit yet to allow atomic operations
        return trade

    def lock_trade(self, trade_id: int) -> Optional[TradeProposal]:
        # Implementa FOR UPDATE para bloquear el renglón (Row Lock) ante condiciones de carrera
        return db.session.query(TradeProposal).filter_by(id=trade_id).with_for_update().first()

    def commit(self) -> None:
        db.session.commit()

    def rollback(self) -> None:
        db.session.rollback()
