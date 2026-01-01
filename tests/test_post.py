def add_post_payload(post_title = "New Post", content = "new post content", user_id = 1, module_id = 1):
    return {"post_title": post_title, "content": content, "user_id": user_id, "module_id": module_id}

def post_payload(post_title = "New Post", content = "new post content", user_id = 1, module_id = 1, id = 1):
    return {"post_title": post_title, "content": content, "user_id": user_id, "module_id": module_id, "id": id, "likes": [], "comments": []}

def user_posts_payload(post_title = "New Post", content = "new post content", user_id = 1, module_id = 1, id = 1):
    return {"post_title": post_title, "content": content, "user_id": user_id, "module_id": module_id, "id": id}

def add_like_payload(user_id = 1, post_id = 1):
    return {"user_id": user_id, "post_id": post_id}

def get_likes_payload(user_id = 1, post_id = 1, id = 1):
    return {"user_id": user_id, "post_id": post_id, "id": id}

def add_comment_payload(user_id = 1, post_id = 1, content = "Great post!"):
    return {"user_id": user_id, "post_id": post_id, "content": content}

def get_comment_payload(user_id = 1, post_id = 1, content = "Great post!", id = 1):
    return {"user_id": user_id, "post_id": post_id, "content": content, "id": id}

############################################################################################################################

###############################POSTS###############################################

def test_add_post_ok(client):
    r = client.post("/api/add-post", json = add_post_payload())
    assert r.status_code == 201
    assert r.json() == post_payload()

#Test after connecting microservices together
# def test_add_post_missing_title(client):
#     r = client.post("/api/add-post", json = add_post_payload(post_title = None))
#     assert r.status_code == 409
#     assert r.json() == {"detail": "Post could not be created"}

def test_get_post_lists_ok(client):
    client.post("/api/add-post", json = add_post_payload())
    r = client.get("/api/get-all-posts")
    assert r.status_code == 200
    assert r.json() == [post_payload()]

def test_get_empty_post_lists(client):
    r = client.get("/api/get-all-posts")
    assert r.status_code == 200
    assert r.json() == []

def test_get_post_by_id_ok(client):
    client.post("/api/add-post", json = add_post_payload())
    r = client.get("/api/post-by-id/1")
    assert r.status_code == 200
    assert r.json() == post_payload()

def test_get_post_by_id_not_found(client):
    client.post("/api/add-post", json = add_post_payload())
    r = client.get("/api/post-by-id/2")
    assert r.status_code == 404
    assert r.json() == {"detail": "Post not found"}

def test_update_post_ok(client):
    client.post("/api/add-post", json = add_post_payload())
    r = client.put("/api/update-post-by-id/1", json = {"post_title": "Updated Post", "content": "updated content", "module_id": 2})
    assert r.status_code == 200
    assert r.json() == {"message": "Post updated successful"}

def test_update_post_not_found(client):
    client.post("/api/add-post", json = add_post_payload())
    r = client.put("/api/update-post-by-id/2", json = {"post_title": "Updated Post", "content": "updated content", "module_id": 2})
    assert r.status_code == 404
    assert r.json() == {"detail": "Post not found"}

def test_delete_post_ok(client):
    client.post("/api/add-post", json = add_post_payload())
    r = client.delete("/api/delete-post-by-id/1")
    assert r.status_code == 204


def test_delete_post_not_found(client):
    client.post("/api/add-post", json = add_post_payload())
    r = client.delete("/api/delete-post-by-id/2")
    assert r.status_code == 404
    assert r.json() == {"detail": "Post not found"}

def test_get_post_by_user_id_ok(client):
    client.post("/api/add-post", json = add_post_payload())
    r = client.get("/api/post-by-user_id/1")
    assert r.status_code == 200
    assert r.json() == [user_posts_payload()]

def test_get_post_by_user_id_no_posts(client):
    r = client.get("/api/post-by-user_id/1")
    assert r.status_code == 404
    assert r.json() == {"detail": "Posts not found for user provided"}

def test_get_post_by_module_id_ok(client):
    client.post("/api/add-post", json = add_post_payload())
    r = client.get("/api/post-by-module_id/1")
    assert r.status_code == 200
    assert r.json() == [user_posts_payload()]

def test_get_post_by_module_id_no_posts(client):
    r = client.get("/api/post-by-module_id/1")
    assert r.status_code == 404
    assert r.json() == {"detail": "Posts not found for module id provided"}

###############################LIKES###############################################

def test_add_like_ok(client):
    client.post("/api/add-post", json = add_post_payload())
    r = client.post("/api/likes", json = add_like_payload())
    assert r.status_code == 201
    response_data = r.json()
    assert response_data["id"] == 1
    assert response_data["user_id"] == 1
    assert response_data["post_id"] == 1
    assert "created_at" in response_data

def test_add_like_not_ok(client):
    client.post("/api/add-post", json = add_post_payload())
    client.post("/api/likes", json = add_like_payload())
    r = client.post("/api/likes", json = add_like_payload())
    assert r.status_code == 409
    assert r.json() == {"detail": "User already liked this post"}

def test_get_all_likes_ok(client):
    client.post("/api/add-post", json = add_post_payload())
    client.post("/api/likes", json = add_like_payload())
    r = client.get("/api/likes")
    assert r.status_code == 200
    response_data = r.json()
    assert len(response_data) == 1
    assert response_data[0]["id"] == 1
    assert response_data[0]["user_id"] == 1
    assert response_data[0]["post_id"] == 1
    assert "created_at" in response_data[0]

def test_get_all_likes_empty(client):
    r = client.get("/api/likes")
    assert r.status_code == 200
    assert r.json() == []

def test_remove_like_ok(client):
    client.post("/api/add-post", json = add_post_payload())
    client.post("/api/likes", json = add_like_payload())
    r = client.delete("/api/likes", params = {"user_id": 1, "post_id": 1})
    assert r.status_code == 200
    assert r.json() == {"message": "Like removed successfully"}

def test_remove_like_not_found(client):
    r = client.delete("/api/likes", params = {"user_id": 1, "post_id": 1})
    assert r.status_code == 404
    assert r.json() == {"detail": "Like not found"}

###############################COMMENTS###############################################

def test_add_comment_ok(client):
    client.post("/api/add-post", json = add_post_payload())
    r = client.post("/api/comments", json = add_comment_payload())
    assert r.status_code == 201
    response_data = r.json()
    assert response_data["id"] == 1
    assert response_data["user_id"] == 1
    assert response_data["post_id"] == 1
    assert response_data["content"] == "Great post!"
    assert "created_at" in response_data

def test_add_comment_not_ok(client):
    r = client.post("/api/comments", json = add_comment_payload())
    assert r.status_code == 409
    assert r.json() == {"detail": "Comment could not be created"}

def test_get_all_comments_ok(client):
    client.post("/api/add-post", json = add_post_payload())
    client.post("/api/comments", json = add_comment_payload())
    r = client.get("/api/comments")
    assert r.status_code == 200
    response_data = r.json()
    assert len(response_data) == 1
    assert response_data[0]["id"] == 1
    assert response_data[0]["user_id"] == 1
    assert response_data[0]["post_id"] == 1
    assert response_data[0]["content"] == "Great post!"
    assert "created_at" in response_data[0]

def test_get_all_comments_empty(client):
    r = client.get("/api/comments")
    assert r.status_code == 200
    assert r.json() == []

def test_get_comments_for_post_ok(client):
    client.post("/api/add-post", json = add_post_payload())
    client.post("/api/comments", json = add_comment_payload())
    r = client.get("/api/comments/1")
    assert r.status_code == 200
    response_data = r.json()
    assert len(response_data) == 1
    assert response_data[0]["id"] == 1
    assert response_data[0]["user_id"] == 1
    assert response_data[0]["post_id"] == 1
    assert response_data[0]["content"] == "Great post!"
    assert "created_at" in response_data[0]

def test_get_comments_for_post_not_found(client):
    r = client.get("/api/comments/1")
    assert r.status_code == 404
    assert r.json() == {"detail": "No comments found for this post"}

def test_get_comments_for_user_ok(client):
    client.post("/api/add-post", json = add_post_payload())
    client.post("/api/comments", json = add_comment_payload())
    r = client.get("/api/comments-by-user/1")
    assert r.status_code == 200
    response_data = r.json()
    assert len(response_data) == 1
    assert response_data[0]["id"] == 1
    assert response_data[0]["user_id"] == 1
    assert response_data[0]["post_id"] == 1
    assert response_data[0]["content"] == "Great post!"
    assert "created_at" in response_data[0]


def test_get_comments_for_user_not_found(client):
    r = client.get("/api/comments-by-user/1")
    assert r.status_code == 404
    assert r.json() == {"detail": "No comments found for this user"}

def test_update_comment_ok(client):
    client.post("/api/add-post", json = add_post_payload())
    client.post("/api/comments", json = add_comment_payload())
    r = client.put("/api/comments/1", json = {"content": "Updated comment content"})
    assert r.status_code == 200
    assert r.json() == {"message": "Comment updated successfully"}

def test_update_comment_not_found(client):
    r = client.put("/api/comments/1", json = {"content": "Updated comment content"})
    assert r.status_code == 404
    assert r.json() == {"detail": "Comment not found"}

def test_delete_comment_ok(client):
    client.post("/api/add-post", json = add_post_payload())
    client.post("/api/comments", json = add_comment_payload())
    r = client.delete("/api/comments/1")
    assert r.status_code == 204

def test_delete_comment_not_found(client):
    r = client.delete("/api/comments/1")
    assert r.status_code == 404
    assert r.json() == {"detail": "Comment not found"}

###############################EVENT HANDLING & INTERNAL LOGIC###############################################

from unittest.mock import AsyncMock, MagicMock, patch
import anyio
from app.main import publish_event, process_user_deleted, process_module_deleted

def test_health_endpoint(client):
    """Test health endpoint"""
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_publish_event_without_rabbit_url():
    """Test publish_event when RABBIT_URL is not set"""
    async def run_test():
        with patch('app.main.RABBIT_URL', None):
            # Should not raise any exception
            await publish_event("test.event", {"data": "test"})

    anyio.run(run_test)


def test_publish_event_with_rabbit_url():
    """Test publish_event when RABBIT_URL is set"""
    async def run_test():
        mock_connection = AsyncMock()
        mock_channel = AsyncMock()
        mock_exchange = AsyncMock()

        mock_connection.__aenter__ = AsyncMock(return_value=mock_connection)
        mock_connection.__aexit__ = AsyncMock(return_value=None)
        mock_connection.channel = AsyncMock(return_value=mock_channel)
        mock_channel.declare_exchange = AsyncMock(return_value=mock_exchange)

        with patch('app.main.RABBIT_URL', 'amqp://localhost'):
            with patch('app.main.aio_pika.connect_robust', return_value=mock_connection):
                await publish_event("test.event", {"data": "test"})

                # Verify exchange was declared and message was published
                mock_channel.declare_exchange.assert_called_once()
                mock_exchange.publish.assert_called_once()

    anyio.run(run_test)


def test_publish_event_connection_failure():
    """Test publish_event when connection fails"""
    async def run_test():
        with patch('app.main.RABBIT_URL', 'amqp://localhost'):
            with patch('app.main.aio_pika.connect_robust', side_effect=Exception("Connection failed")):
                # Should not raise exception, just print error
                await publish_event("test.event", {"data": "test"})

    anyio.run(run_test)


def test_process_user_deleted_no_user_id():
    """Test process_user_deleted with no user_id in data"""
    async def run_test():
        await process_user_deleted({})

    anyio.run(run_test)


def test_process_user_deleted_with_user_id(client):
    """Test process_user_deleted removes all user data"""
    from conftest import TestingSessionLocal

    async def run_test():
        # Setup: Create a post, like, and comment for user_id=1
        client.post("/api/add-post", json={"post_title": "Test Post", "content": "test content", "user_id": 1, "module_id": 1})
        client.post("/api/likes", json={"user_id": 1, "post_id": 1})
        client.post("/api/comments", json={"user_id": 1, "post_id": 1, "content": "Test comment"})

        # Verify data exists
        posts_before = client.get("/api/post-by-user_id/1")
        assert posts_before.status_code == 200
        assert len(posts_before.json()) == 1

        # Process user deletion with test database
        with patch('app.main.SessionLocal', TestingSessionLocal):
            await process_user_deleted({"user_id": 1})

        # Verify data is deleted
        posts_after = client.get("/api/post-by-user_id/1")
        assert posts_after.status_code == 404

        likes_after = client.get("/api/likes")
        assert likes_after.json() == []

        comments_after = client.get("/api/comments")
        assert comments_after.json() == []

    anyio.run(run_test)


def test_process_user_deleted_db_error():
    """Test process_user_deleted handles database errors"""
    async def run_test():
        mock_db = MagicMock()
        mock_db.query.side_effect = Exception("Database error")

        with patch('app.main.SessionLocal', return_value=mock_db):
            # Should not raise exception, just rollback and close
            await process_user_deleted({"user_id": 1})
            mock_db.rollback.assert_called_once()
            mock_db.close.assert_called_once()

    anyio.run(run_test)


def test_process_module_deleted_no_module_id():
    """Test process_module_deleted with no module_id in data"""
    async def run_test():
        await process_module_deleted({})

    anyio.run(run_test)


def test_process_module_deleted_with_module_id(client):
    """Test process_module_deleted removes all module posts"""
    from conftest import TestingSessionLocal

    async def run_test():
        # Setup: Create posts for module_id=1
        client.post("/api/add-post", json={"post_title": "Test Post 1", "content": "test content", "user_id": 1, "module_id": 1})
        client.post("/api/add-post", json={"post_title": "Test Post 2", "content": "test content", "user_id": 2, "module_id": 1})

        # Verify data exists
        posts_before = client.get("/api/post-by-module_id/1")
        assert posts_before.status_code == 200
        assert len(posts_before.json()) == 2

        # Process module deletion with test database
        with patch('app.main.SessionLocal', TestingSessionLocal):
            await process_module_deleted({"module_id": 1})

        # Verify data is deleted
        posts_after = client.get("/api/post-by-module_id/1")
        assert posts_after.status_code == 404

    anyio.run(run_test)


def test_process_module_deleted_db_error():
    """Test process_module_deleted handles database errors"""
    async def run_test():
        mock_db = MagicMock()
        mock_db.query.side_effect = Exception("Database error")

        with patch('app.main.SessionLocal', return_value=mock_db):
            # Should not raise exception, just rollback and close
            await process_module_deleted({"module_id": 1})
            mock_db.rollback.assert_called_once()
            mock_db.close.assert_called_once()

    anyio.run(run_test)