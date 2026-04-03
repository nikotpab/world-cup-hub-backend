from app.application.interfaces.trade_repository import ITradeRepository
from app.application.dtos.trade_dto import TradeProposeDTO, TradeResponseDTO
from app.domain.models.trade_proposal import TradeProposal
import logging

logger = logging.getLogger(__name__)

class TradeService:
    def __init__(self, repository: ITradeRepository):
        self.repository = repository

    def propose_trade(self, data: dict) -> TradeResponseDTO:
        dto = TradeProposeDTO(**data)
        
        try:
            trade = TradeProposal(
                proposer_id=dto.proposer_id,
                receiver_id=dto.receiver_id,
                offered_sticker_id=dto.offered_sticker_id,
                requested_sticker_id=dto.requested_sticker_id,
                status='PENDING_CONFIRMATION'
            )
            saved_trade = self.repository.save(trade)
            self.repository.commit()
            
            logger.info({"event": "trade_proposed", "trade_id": saved_trade.id})
            return TradeResponseDTO.model_validate(saved_trade)
            
        except Exception as e:
            self.repository.rollback()
            raise ValueError(f"No se pudo proponer el intercambio: {str(e)}")

    def confirm_trade(self, trade_id: int) -> TradeResponseDTO:
        try:
            # 1. Row Lock explícito en la base de datos (con with_for_update())
            trade = self.repository.lock_trade(trade_id)
            
            if not trade:
                raise ValueError("Trade not found")
                
            if trade.status != 'PENDING_CONFIRMATION':
                raise ValueError(f"Trade is already in status: {trade.status}")
                
            # 2. Mutar el estado a completado
            trade.status = 'COMPLETED'
            saved_trade = self.repository.save(trade)
            
            # --- Aquí iría la lógica cruzada para quitar el sticker al proposer y dárselo al receiver ---
            # ej: user_repo.transfer_sticker(trade.proposer_id, trade.receiver_id, trade.offered_sticker_id)
            
            # 3. Commit transaccional atómico
            self.repository.commit()
            
            logger.info({"event": "trade_confirmed", "trade_id": saved_trade.id})
            return TradeResponseDTO.model_validate(saved_trade)
            
        except Exception as e:
            self.repository.rollback()
            logger.error({"event": "trade_confirmation_failed", "trade_id": trade_id, "error": str(e)})
            raise ValueError(f"Error confirmando intercambio: {str(e)}")
