from src.database import db
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema 
from marshmallow import fields

class Album(db.Model):
    __tablename__ = "ALBUM"
    
    albumId = db.Column(db.Integer, primary_key=True, autoincrement=True)
    
    def create(self):
        db.session.add(self)
        db.session.commit()
        return self

class AlbumSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Album
        load_instance = True  
        sqla_session = db.session
