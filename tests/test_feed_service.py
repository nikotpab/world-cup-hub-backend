import pytest
from unittest.mock import patch, MagicMock
from app.application.services.feed_service import FeedService
from app.domain.models.user import User
from app.domain.models.post import Post
from app.infrastructure.database import db

@pytest.fixture
def feed_service():
    return FeedService()

@pytest.fixture
def test_user():
    user = User(
        firstName="Feed",
        lastName="User",
        email="feeduser@example.com",
        password="password",
        identification=11112222
    )
    db.session.add(user)
    db.session.commit()
    return user

def test_create_post(test_user, feed_service):
    post_dict = feed_service.create_post(
        user_id=test_user.idUser,
        content="Testing post creation",
        images=[]
    )
    assert post_dict["content"] == "Testing post creation"
    assert post_dict["user"]["id"] == test_user.idUser

@patch("app.infrastructure.external.notification_service.NotificationService.broadcast_to_topic")
def test_edit_post_broadcasts(mock_broadcast, test_user, feed_service):
    post_dict = feed_service.create_post(
        user_id=test_user.idUser,
        content="Original Content",
        images=[]
    )
    
    updated_dict = feed_service.edit_post(
        post_id=post_dict["id"],
        user_id=test_user.idUser,
        content="Updated Content"
    )
    
    assert updated_dict["content"] == "Updated Content"
    mock_broadcast.assert_called_once_with(
        topic="feed",
        data={
            "notif_type": "post_edited",
            "post_id": post_dict["id"],
            "content": "Updated Content"
        }
    )

@patch("app.infrastructure.external.notification_service.NotificationService.broadcast_to_topic")
def test_delete_post_broadcasts(mock_broadcast, test_user, feed_service):
    post_dict = feed_service.create_post(
        user_id=test_user.idUser,
        content="To be deleted",
        images=[]
    )
    
    feed_service.delete_post(
        post_id=post_dict["id"],
        user_id=test_user.idUser
    )
    
    post = Post.query.get(post_dict["id"])
    assert post is None
    
    mock_broadcast.assert_called_once_with(
        topic="feed",
        data={
            "notif_type": "post_deleted",
            "post_id": post_dict["id"]
        }
    )
