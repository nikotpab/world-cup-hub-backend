from src.database import db
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema 
from marshmallow import fields

class Prediction(db.Model):
    __tablename__ = "PREDICTION"
    
    predictionId = db.Column(db.Integer, primary_key=True, autoincrement=True)
    homeGoals = db.Column(db.Integer, nullable=False)
    awayGoals = db.Column(db.Integer, nullable=False)
    
    def create(self):
        db.session.add(self)
        db.session.commit()
        return self

class PredictionSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Prediction
        load_instance = True  
        sqla_session = db.session
