from app.infrastructure.database import db

class PostImage(db.Model):
    __tablename__ = "post_image"
    id         = db.Column(db.Integer, primary_key=True, autoincrement=True)
    post_id    = db.Column(db.Integer, db.ForeignKey('post.id', ondelete='CASCADE'), nullable=False)
    image_data = db.Column(db.Text, nullable=False)
    position   = db.Column(db.Integer, default=0)

    post = db.relationship('Post', back_populates='images')
