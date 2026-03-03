from flask_sqlalchemy import SQLAlchemy
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema 
from marshmallow import fields

db = SQLAlchemy()


class Billetera(db.Model):
    __tablename__ = "BILLETERA"
    
    IdBilletera = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Saldo = db.Column(db.Float, nullable=False)

    
    def create(self):
        db.session.add(self)
        db.session.commit()
        return self


class BilleteraSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Billetera
        load_instance = True  
        sqla_session = db.session

