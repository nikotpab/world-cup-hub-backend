from app.infrastructure.database import db
from datetime import datetime, timezone

class Post(db.Model):
    __tablename__ = "post"
    id         = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id    = db.Column(db.Integer, db.ForeignKey('USER.iduser'), nullable=False)
    group_id   = db.Column(db.Integer, db.ForeignKey('pool_group.id_group', ondelete='CASCADE'), nullable=True)
    content    = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    user    = db.relationship('User', backref='posts')
    images  = db.relationship('PostImage',   back_populates='post', cascade='all, delete-orphan', order_by='PostImage.position')
    likes   = db.relationship('PostLike',    back_populates='post', cascade='all, delete-orphan')
    comments= db.relationship('PostComment', back_populates='post', cascade='all, delete-orphan')
