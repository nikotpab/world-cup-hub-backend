from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from app.infrastructure.database import db
from app.domain.models.post import Post
from app.domain.models.post_image import PostImage
from app.domain.models.post_like import PostLike
from app.domain.models.post_comment import PostComment
from app.domain.models.comment_like import CommentLike
from app.domain.models.user import User


def _user_dict(user: User) -> Dict:
    pic = getattr(user, 'profilePicture', None)
    return {
        "id":        user.idUser,
        "firstName": user.firstName,
        "lastName":  user.lastName,
        "avatar":    pic,
    }


def _comment_dict(c: PostComment, viewer_id: int) -> Dict:
    liked = any(l.user_id == viewer_id for l in c.likes)
    return {
        "id":         c.id,
        "content":    c.content,
        "createdAt":  c.created_at.isoformat() if c.created_at else None,
        "user":       _user_dict(c.user),
        "likeCount":  len(c.likes),
        "likedByMe":  liked,
        "parentId":   c.parent_id,
        "replies":    [_comment_dict(r, viewer_id) for r in
                       sorted(c.replies, key=lambda x: x.created_at or datetime.min)],
    }


def _post_dict(post: Post, viewer_id: int) -> Dict:
    liked = any(l.user_id == viewer_id for l in post.likes)
    return {
        "id":           post.id,
        "content":      post.content or "",
        "createdAt":    post.created_at.isoformat() if post.created_at else None,
        "user":         _user_dict(post.user),
        "images":       [img.image_data for img in post.images],
        "likeCount":    len(post.likes),
        "likedByMe":    liked,
        "commentCount": len([c for c in post.comments if c.parent_id is None]),
    }


class FeedService:
    _ERR_POST_NOT_FOUND = "Publicación no encontrada."

    # ── Posts ────────────────────────────────────────────────────────────────

    def get_feed(self, viewer_id: int, page: int = 1, per_page: int = 20,
                 group_id: Optional[int] = None) -> List[Dict]:
        q = Post.query.order_by(Post.created_at.desc())
        if group_id is not None:
            q = q.filter(Post.group_id == group_id)
        else:
            q = q.filter(Post.group_id == None)  # noqa: E711 global feed
        posts = q.offset((page - 1) * per_page).limit(per_page).all()
        return [_post_dict(p, viewer_id) for p in posts]

    def create_post(self, user_id: int, content: str, images: List[str],
                    group_id: Optional[int] = None) -> Dict:
        if not content.strip() and not images:
            raise ValueError("La publicación debe tener texto o al menos una imagen.")
        post = Post(user_id=user_id, content=content.strip(), group_id=group_id)
        db.session.add(post)
        db.session.flush()
        for i, img_data in enumerate(images[:4]):
            db.session.add(PostImage(post_id=post.id, image_data=img_data, position=i))
        db.session.commit()
        db.session.refresh(post)
        return _post_dict(post, user_id)

    def edit_post(self, post_id: int, user_id: int, content: str) -> Dict:
        post = Post.query.get(post_id)
        if not post:
            raise ValueError(self._ERR_POST_NOT_FOUND)
        if post.user_id != user_id:
            raise PermissionError("No puedes editar esta publicación.")
        post.content = content.strip()
        db.session.commit()
        db.session.refresh(post)
        return _post_dict(post, user_id)

    def delete_post(self, post_id: int, user_id: int) -> None:
        post = Post.query.get(post_id)
        if not post:
            raise ValueError(self._ERR_POST_NOT_FOUND)
        if post.user_id != user_id:
            raise PermissionError("No puedes eliminar esta publicación.")
        db.session.delete(post)
        db.session.commit()

    def toggle_like(self, post_id: int, user_id: int) -> Dict:
        post = Post.query.get(post_id)
        if not post:
            raise ValueError(self._ERR_POST_NOT_FOUND)
        existing = PostLike.query.filter_by(post_id=post_id, user_id=user_id).first()
        if existing:
            db.session.delete(existing)
            liked = False
        else:
            db.session.add(PostLike(post_id=post_id, user_id=user_id))
            liked = True
        db.session.commit()
        count = PostLike.query.filter_by(post_id=post_id).count()

        if liked and post.user_id != user_id:
            try:
                from app.infrastructure.external.notification_service import notification_service
                liker = User.query.get(user_id)
                name = liker.firstName if liker else "Alguien"
                notification_service.notify_user_from_id(
                    user_id=post.user_id,
                    title="❤️ Nueva reacción",
                    body=f"A {name} le gustó tu publicación.",
                    notif_type="community_like",
                    reference_id=post_id,
                    reference_type="post",
                    channels=["push"],
                )
            except Exception:
                pass

        return {"liked": liked, "likeCount": count}

    # ── Comments ─────────────────────────────────────────────────────────────

    def get_comments(self, post_id: int, viewer_id: int) -> List[Dict]:
        top_level = (PostComment.query
                     .filter_by(post_id=post_id, parent_id=None)
                     .order_by(PostComment.created_at.asc())
                     .all())
        return [_comment_dict(c, viewer_id) for c in top_level]

    def add_comment(self, post_id: int, user_id: int,
                    content: str, parent_id: Optional[int] = None) -> Dict:
        if not content.strip():
            raise ValueError("El comentario no puede estar vacío.")
        if not Post.query.get(post_id):
            raise ValueError(self._ERR_POST_NOT_FOUND)
        if parent_id and not PostComment.query.get(parent_id):
            raise ValueError("Comentario padre no encontrado.")
        c = PostComment(post_id=post_id, user_id=user_id,
                        content=content.strip(), parent_id=parent_id)
        db.session.add(c)
        db.session.commit()
        db.session.refresh(c)

        try:
            from app.infrastructure.external.notification_service import notification_service
            post = Post.query.get(post_id)
            commenter = User.query.get(user_id)
            commenter_name = commenter.firstName if commenter else "Alguien"
            snippet = content.strip()[:60] + ("..." if len(content.strip()) > 60 else "")

            # Notificar al autor del post (si no es el mismo)
            if post and post.user_id != user_id:
                notification_service.notify_user_from_id(
                    user_id=post.user_id,
                    title="💬 Nuevo comentario",
                    body=f"{commenter_name} comentó tu publicación: \"{snippet}\"",
                    notif_type="community_comment",
                    reference_id=post_id,
                    reference_type="post",
                    channels=["push"],
                )

            # Notificar al autor del comentario padre si es una respuesta
            if parent_id:
                parent = PostComment.query.get(parent_id)
                if parent and parent.user_id != user_id:
                    notification_service.notify_user_from_id(
                        user_id=parent.user_id,
                        title="↩️ Alguien respondió tu comentario",
                        body=f"{commenter_name} respondió: \"{snippet}\"",
                        notif_type="community_reply",
                        reference_id=post_id,
                        reference_type="post",
                        channels=["push"],
                    )
        except Exception:
            pass

        return _comment_dict(c, user_id)

    def delete_comment(self, comment_id: int, user_id: int) -> None:
        c = PostComment.query.get(comment_id)
        if not c:
            raise ValueError("Comentario no encontrado.")
        if c.user_id != user_id:
            raise PermissionError("No puedes eliminar este comentario.")
        db.session.delete(c)
        db.session.commit()

    def toggle_comment_like(self, comment_id: int, user_id: int) -> Dict:
        if not PostComment.query.get(comment_id):
            raise ValueError("Comentario no encontrado.")
        existing = CommentLike.query.filter_by(comment_id=comment_id, user_id=user_id).first()
        if existing:
            db.session.delete(existing)
            liked = False
        else:
            db.session.add(CommentLike(comment_id=comment_id, user_id=user_id))
            liked = True
        db.session.commit()
        count = CommentLike.query.filter_by(comment_id=comment_id).count()
        return {"liked": liked, "likeCount": count}


feed_service = FeedService()
