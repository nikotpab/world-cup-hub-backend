from app.infrastructure.database import db
from datetime import datetime, timezone

class PostLike(db.Model):
    __tablename__ = "post_like"
    post_id    = db.Column(db.Integer, db.ForeignKey('post.id', ondelete='CASCADE'), primary_key=True)
    user_id    = db.Column(db.Integer, db.ForeignKey('USER.iduser'), primary_key=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    post = db.relationship('Post', back_populates='likes')
