from typing import List
from sqlalchemy.orm.exc import StaleDataError
from app.application.interfaces.betting_repository import IBettingRepository
from app.application.dtos.betting_dto import PredictionCreateDTO, PredictionUpdateDTO, PredictionResponseDTO
from app.domain.models.prediction import Prediction
import logging

logger = logging.getLogger(__name__)

class BettingService:
    def __init__(self, repository: IBettingRepository):
        self.repository = repository

    def create_prediction(self, data: dict) -> PredictionResponseDTO:
        dto = PredictionCreateDTO(**data)
        
        try:
            prediction = Prediction(
                homeGoals=dto.homeGoals,
                awayGoals=dto.awayGoals,
                bettingPoolId=dto.bettingPoolId,
                matchId=dto.matchId,
                userId=dto.userId
            )
            saved_pred = self.repository.save_prediction(prediction)
            self.repository.commit()
            return PredictionResponseDTO.model_validate(saved_pred)
            
        except Exception as e:
            self.repository.rollback()
            raise ValueError(f"No se pudo registrar la predicción: {str(e)}")

    def update_prediction(self, prediction_id: int, data: dict) -> PredictionResponseDTO:
        dto = PredictionUpdateDTO(**data)
        
        try:
            prediction = self.repository.get_prediction_by_id(prediction_id)
            if not prediction:
                raise ValueError("Prediction not found")
                
            prediction.homeGoals = dto.homeGoals
            prediction.awayGoals = dto.awayGoals
            
            # Flush evalúa el optimistic locking (version_id)
            self.repository.flush()
            self.repository.commit()
            return PredictionResponseDTO.model_validate(prediction)
            
        except StaleDataError:
            self.repository.rollback()
            logger.warning({"event": "optimistic_lock_collision", "prediction_id": prediction_id})
            # El backend lanza el error para que el frontend intente denuevo o informe que el recurso expiró
            raise RuntimeError("Collision detected. La predicción ha sido modificada por otra transacción. Refresca y reintenta.")
        except Exception as e:
            self.repository.rollback()
            raise ValueError(f"Error actualizando pronóstico: {str(e)}")
