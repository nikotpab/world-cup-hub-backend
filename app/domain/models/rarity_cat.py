from app.infrastructure.database import db

class RarityCat(db.Model):
    __tablename__ = "raryty_cat"
    
    rarityCatId = db.Column('rarety_cat_id', db.Integer, primary_key=True, autoincrement=True)
    name = db.Column('name', db.String(100), nullable=False)

    def save(self):
        db.session.add(self)
        db.session.commit()
        return self
