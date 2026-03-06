from src.database import db
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema 
from marshmallow import fields

class Event(db.Model):
    __tablename__ = "EVENT"
    
    eventId = db.Column(db.Integer, primary_key=True, autoincrement=True)
    type = db.Column(db.String(1), nullable=False)
    description = db.Column(db.String(200), nullable=False)
    
    def create(self):
        db.session.add(self)
        db.session.commit()
        return self

class EventSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Event
        load_instance = True  
        sqla_session = db.session
