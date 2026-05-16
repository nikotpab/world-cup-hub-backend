from app.infrastructure.database import db
from datetime import datetime, timezone

class CommentLike(db.Model):
    __tablename__ = "comment_like"
    comment_id = db.Column(db.Integer, db.ForeignKey('post_comment.id', ondelete='CASCADE'), primary_key=True)
    user_id    = db.Column(db.Integer, db.ForeignKey('USER.iduser'), primary_key=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    comment = db.relationship('PostComment', back_populates='likes')
