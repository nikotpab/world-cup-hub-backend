from app.infrastructure.database import db
from datetime import datetime, timezone

class PostComment(db.Model):
    __tablename__ = "post_comment"
    id         = db.Column(db.Integer, primary_key=True, autoincrement=True)
    post_id    = db.Column(db.Integer, db.ForeignKey('post.id', ondelete='CASCADE'), nullable=False)
    user_id    = db.Column(db.Integer, db.ForeignKey('USER.iduser'), nullable=False)
    content    = db.Column(db.Text, nullable=False)
    parent_id  = db.Column(db.Integer, db.ForeignKey('post_comment.id', ondelete='CASCADE'), nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    post    = db.relationship('Post', back_populates='comments')
    user    = db.relationship('User', backref='comments')
    likes   = db.relationship('CommentLike', back_populates='comment', cascade='all, delete-orphan')
    replies = db.relationship('PostComment', backref=db.backref('parent', remote_side=[id]),
                              cascade='all, delete-orphan')
