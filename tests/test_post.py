def add_post_payload(post_title = "New Post", content = "new post content", user_id = 1, module_id = 1):
    return {"post_title": post_title, "content": content, "user_id": user_id, "module_id": module_id}

def post_payload(post_title = "New Post", content = "new post content", user_id = 1, module_id = 1, id = 1):
    return {"post_title": post_title, "content": content, "user_id": user_id, "module_id": module_id, "id": id}

def user_posts_payload(post_title = "New Post", content = "new post content", user_id = 1, module_id = 1):
    return {"post_title": post_title, "content": content, "user_id": user_id, "module_id": module_id}

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
    assert r.status_code == 200
    assert r.json() == {"message": "Deleted Post"}

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
    assert r.json() == get_likes_payload()

def test_add_like_not_ok(client):
    client.post("/api/likes", json = add_like_payload())
    r = client.post("/api/likes", json = add_like_payload())
    assert r.status_code == 409
    assert r.json() == {"detail": "User already liked this post"}

def test_get_all_likes_ok(client):
    client.post("/api/add-post", json = add_post_payload())
    client.post("/api/likes", json = add_like_payload())
    r = client.get("/api/likes")
    assert r.status_code == 200
    assert r.json() == [get_likes_payload()]

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
    assert r.json() == get_comment_payload()

def test_add_comment_not_ok(client):
    r = client.post("/api/comments", json = add_comment_payload())
    assert r.status_code == 409
    assert r.json() == {"detail": "Comment could not be created"}

def test_get_all_comments_ok(client):
    client.post("/api/add-post", json = add_post_payload())
    client.post("/api/comments", json = add_comment_payload())
    r = client.get("/api/comments")
    assert r.status_code == 200
    assert r.json() == [get_comment_payload()]

def test_get_all_comments_empty(client):
    r = client.get("/api/comments")
    assert r.status_code == 200
    assert r.json() == []

def test_get_comments_for_post_ok(client):
    client.post("/api/add-post", json = add_post_payload())
    client.post("/api/comments", json = add_comment_payload())
    r = client.get("/api/comments/1")
    assert r.status_code == 200
    assert r.json() == [get_comment_payload()]

def test_get_comments_for_post_not_found(client):
    r = client.get("/api/comments/1")
    assert r.status_code == 404
    assert r.json() == {"detail": "No comments found for this post"}

def test_get_comments_for_user_ok(client):
    client.post("/api/add-post", json = add_post_payload())
    client.post("/api/comments", json = add_comment_payload())
    r = client.get("/api/comments/1")
    assert r.status_code == 200
    assert r.json() == [get_comment_payload()]

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
    assert r.status_code == 200
    assert r.json() == {"message": "Comment deleted successfully"}

def test_delete_comment_not_found(client):
    r = client.delete("/api/comments/1")
    assert r.status_code == 404
    assert r.json() == {"detail": "Comment not found"}