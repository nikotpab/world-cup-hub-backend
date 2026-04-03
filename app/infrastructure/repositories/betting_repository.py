from typing import Optional, List, Dict, Any
from app.application.interfaces.betting_repository import IBettingRepository
from app.domain.models.prediction import Prediction
from app.infrastructure.database import db

class SqlAlchemyBettingRepository(IBettingRepository):
    def get_prediction_by_id(self, prediction_id: int) -> Optional[Prediction]:
        return Prediction.query.get(prediction_id)

    def save_prediction(self, prediction: Prediction) -> Prediction:
        db.session.add(prediction)
        return prediction

    def flush(self) -> None:
        db.session.flush()

    def commit(self) -> None:
        db.session.commit()

    def rollback(self) -> None:
        db.session.rollback()
