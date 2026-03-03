from flask_sqlalchemy import SQLAlchemy
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema 
from marshmallow import fields

db = SQLAlchemy()


class Album(db.Model):
    __tablename__ = "ALBUM"
    
    IdAlbum = db.Column(db.Integer, primary_key=True, autoincrement=True)

    
    def create(self):
        db.session.add(self)
        db.session.commit()
        return self


class AlbumSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Album
        load_instance = True  
        sqla_session = db.session

