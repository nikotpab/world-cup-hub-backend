from app.application.interfaces.trade_repository import ITradeRepository
from app.application.dtos.trade_dto import TradeProposeDTO, TradeResponseDTO
from app.domain.models.trade_proposal import TradeProposal
from app.domain.models.pack import Pack, pack_sticker
from app.domain.models.album import Album, sticker_album
from app.infrastructure.database import db
from datetime import datetime, date
import logging

logger = logging.getLogger(__name__)

class TradeService:
    def __init__(self, repository: ITradeRepository):
        self.repository = repository

    def propose_trade(self, data: dict) -> TradeResponseDTO:
        from app.domain.models.user import User
        from app.infrastructure.external.notification_service import notification_service
        
        dto = TradeProposeDTO(**data)
        
        # Resolve receiver_id from email
        receiver = User.query.filter_by(email=dto.receiver_email).first()
        if not receiver:
            raise ValueError(f"No se encontró un usuario con el correo: {dto.receiver_email}")
            
        if receiver.idUser == dto.proposer_id:
            raise ValueError("No puedes intercambiar láminas contigo mismo.")
        
        # Check daily trade limit
        today_start = datetime.combine(date.today(), datetime.min.time())
        daily_trades_count = TradeProposal.query.filter(
            TradeProposal.proposer_id == dto.proposer_id,
            TradeProposal.status == 'COMPLETED',
            TradeProposal.updated_at >= today_start
        ).count()
        
        if daily_trades_count >= 5:
            raise ValueError("Has alcanzado el límite diario de intercambios (5).")

        try:
            trade = TradeProposal(
                proposer_id=dto.proposer_id,
                receiver_id=receiver.idUser,
                offered_sticker_id=dto.offered_sticker_id,
                requested_sticker_id=dto.requested_sticker_id,
                status='PENDING_CONFIRMATION'
            )
            saved_trade = self.repository.save(trade)
            self.repository.commit()
            
            logger.info({"event": "trade_proposed", "trade_id": saved_trade.id})
            
            # Send notification
            notification_service.notify_user_from_id(
                user_id=receiver.idUser,
                title="Nueva solicitud de intercambio",
                body=f"Un usuario quiere intercambiar su lámina #{dto.offered_sticker_id} por tu lámina #{dto.requested_sticker_id}. Ingresa a la app para aceptar o rechazar.",
                notif_type="trade",
                reference_id=saved_trade.id,
                reference_type="trade_proposal"
            )
            
            return TradeResponseDTO.model_validate(saved_trade)
            
        except Exception as e:
            self.repository.rollback()
            raise ValueError(f"No se pudo proponer el intercambio: {str(e)}")

    def confirm_trade(self, trade_id: int) -> TradeResponseDTO:
        try:
            trade = self.repository.lock_trade(trade_id)
            
            if not trade:
                raise ValueError("Trade not found")
                
            if trade.status != 'PENDING_CONFIRMATION':
                raise ValueError(f"Trade is already in status: {trade.status}")
                
            today_start = datetime.combine(date.today(), datetime.min.time())
            receiver_trades_count = TradeProposal.query.filter(
                TradeProposal.receiver_id == trade.receiver_id,
                TradeProposal.status == 'COMPLETED',
                TradeProposal.updated_at >= today_start
            ).count()
            
            if receiver_trades_count >= 5:
                raise ValueError("El destinatario ha alcanzado su límite diario de intercambios.")

            # 2. Transfer logic: Reassign stickers
            proposer_album = Album.query.filter_by(idUser=trade.proposer_id).first()
            receiver_album = Album.query.filter_by(idUser=trade.receiver_id).first()
            
            if not proposer_album or not receiver_album:
                raise ValueError("Álbum de proponente o receptor no encontrado.")

            # Find offered sticker association in proposer's album
            offered_assoc = db.session.query(sticker_album).filter_by(
                id_album=proposer_album.idAlbum, 
                id_sticker=trade.offered_sticker_id
            ).first()
            
            if not offered_assoc:
                raise ValueError("El proponente ya no tiene la lámina ofrecida.")

            # Find requested sticker association in receiver's album
            requested_assoc = db.session.query(sticker_album).filter_by(
                id_album=receiver_album.idAlbum, 
                id_sticker=trade.requested_sticker_id
            ).first()
            
            if not requested_assoc:
                raise ValueError("El destinatario ya no tiene la lámina solicitada.")

            # ATOMIC SWAP
            # Move offered: Proposer -> Receiver
            db.session.execute(
                sticker_album.update().where(sticker_album.c.id == offered_assoc.id).values(id_album=receiver_album.idAlbum)
            )
            # Move requested: Receiver -> Proposer
            db.session.execute(
                sticker_album.update().where(sticker_album.c.id == requested_assoc.id).values(id_album=proposer_album.idAlbum)
            )

            trade.status = 'COMPLETED'
            trade.updated_at = datetime.utcnow()
            saved_trade = self.repository.save(trade)

            self.repository.commit()

            logger.info({"event": "trade_confirmed", "trade_id": saved_trade.id})

            # Notificar al proponente que su intercambio fue aceptado
            try:
                from app.domain.models.sticker import Sticker
                from app.infrastructure.external.notification_service import notification_service
                offered = Sticker.query.get(trade.offered_sticker_id)
                requested = Sticker.query.get(trade.requested_sticker_id)
                offered_name = offered.name if offered else f"#{trade.offered_sticker_id}"
                requested_name = requested.name if requested else f"#{trade.requested_sticker_id}"
                notification_service.notify_user_from_id(
                    user_id=trade.proposer_id,
                    title="¡Intercambio aceptado! 🤝",
                    body=f"Tu propuesta fue aceptada. Cambiaste '{offered_name}' por '{requested_name}'.",
                    notif_type="trade_accepted",
                    reference_id=saved_trade.id,
                    reference_type="trade_proposal",
                )
            except Exception:
                pass

            return TradeResponseDTO.model_validate(saved_trade)
            
        except Exception as e:
            self.repository.rollback()
            logger.error({"event": "trade_confirmation_failed", "trade_id": trade_id, "error": str(e)})
            raise ValueError(f"Error confirmando intercambio: {str(e)}")
