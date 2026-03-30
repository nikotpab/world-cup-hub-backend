from src.database import db
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema

class RarityCat(db.Model):
    __tablename__ = "RARYTY_CAT"
    
    rarityCatId = db.Column('rarety_cat_id', db.Integer, primary_key=True, autoincrement=True)
    name = db.Column('name', db.String(100), nullable=False)
    
    def create(self):
        db.session.add(self)
        db.session.commit()
        return self

class RarityCatSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = RarityCat
        load_instance = True
        sqla_session = db.session
