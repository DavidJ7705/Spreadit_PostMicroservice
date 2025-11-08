# app/main.py
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException, status, Response
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine
from app.models import Base, PostDB, LikeDB, CommentDB
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, selectinload

from .database import engine, SessionLocal
from .schemas import Post, AddPost, UpdatePost, UserPosts, Like, AddLike, Comment, AddComment

#Replacing @app.on_event("startup")
@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)   
    yield

app = FastAPI(lifespan=lifespan)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def commit_or_rollback(db: Session, error_msg: str):
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail=error_msg)

@app.get("/health")
def health():
    return {"status": "ok"}


#------------- No Id functions -------------#
#Add Post
@app.post("/api/add-post", response_model=AddPost, status_code=status.HTTP_201_CREATED)
def add_post(payload: AddPost, db: Session = Depends(get_db)):
    post = PostDB(**payload.model_dump())
    db.add(post)

    commit_or_rollback(db, "Post could not be created")
    return post

#using db to get all posts
@app.get("/api/get-all-posts", response_model=list[Post])
def get_posts(db: Session = Depends(get_db)):
    stmt = select(PostDB).order_by(PostDB.id)
    return list(db.execute(stmt).scalars())


#------------- Posts Backend Id based functions -------------#
#get post by its backend id  
@app.get("/api/post-by-id/{id}", response_model=Post)
def get_post(id: str, db: Session = Depends(get_db)):
    post = db.query(PostDB).filter(PostDB.id == id).first()
    if not post: 
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found") #if not found return 404
    return post

#update post by backend id
@app.put("/api/update-post-by-id/{id}", status_code=status.HTTP_200_OK)
def update_post(id: str, updated_post: UpdatePost, db: Session = Depends(get_db)):
    result = db.query(PostDB).filter(PostDB.id == id).update(updated_post.model_dump())
    db.commit()

    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="post not found")

    return {"message": "Post updated successful"}

#delete post by backend id
@app.delete("/api/delete-post-by-id/{id}", status_code=status.HTTP_200_OK)
def delete_post(id: str, db: Session = Depends(get_db)):
    post = db.query(PostDB).filter(PostDB.id == id).first()
    db.delete(post)
    db.commit()

    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

    return {"message": "Deleted Post"}

#------------- Posts User Id based functions -------------#

#get posts by its user id  
@app.get("/api/post-by-user_id/{user_id}", response_model=list[UserPosts])
def get_post(user_id: str, db: Session = Depends(get_db)):
    post = db.query(PostDB).filter(PostDB.user_id == user_id).all()
    if not post: 
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Posts not found for user id provided")
    return post

#update post by user id
@app.put("/api/update-post-by-user-id/{user_id}", status_code=status.HTTP_200_OK)
def update_post(user_id: str, updated_post: UpdatePost, db: Session = Depends(get_db)):
    result = db.query(PostDB).filter(PostDB.user_id == user_id).update(updated_post.model_dump())
    db.commit()

    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="post not found")

    return {"message": "Post updated successful"}

#update specific post by post id & user id
@app.put("/api/update-specific-post/user/{user_id}/{id}", status_code=status.HTTP_200_OK)
def update_specific_user_post(user_id: str, id:int, updated_post: UpdatePost, db: Session = Depends(get_db)):
    post = db.query(PostDB).filter(
        PostDB.user_id == user_id,
        PostDB.id == id).update(updated_post.model_dump())
    db.commit()

    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="post not found")

    return {"message": "Post updated successful"}



#delete post by user id
@app.delete("/api/delete-post-by-user-id/{user_id}", status_code=status.HTTP_200_OK)
def delete_post(user_id: str, db: Session = Depends(get_db)):
    post = db.query(PostDB).filter(PostDB.user_id == user_id).first()
    db.delete(post)
    db.commit()

    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

    return {"message": "Deleted Post"}

#delete specific post by id & user id
@app.delete("/api/delete-specific-post/user/{user_id}/{id}", status_code=status.HTTP_200_OK)
def delete_specific_post(user_id: str, id:int, db: Session = Depends(get_db)):
    post = db.query(PostDB).filter(
        PostDB.user_id == user_id,
        PostDB.id == id).first()
    db.delete(post)
    db.commit()

    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

    return {"message": "Deleted Post"}

#------------- Posts Module Id based functions -------------#

#get posts by its module id  
@app.get("/api/post-by-module_id/{module_id}", response_model=list[UserPosts])
def get_post(module_id: str, db: Session = Depends(get_db)):
    post = db.query(PostDB).filter(PostDB.module_id == module_id).all()
    if not post: 
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Posts not found for module id provided")
    return post

#update post by module id
@app.put("/api/update-post-by-module-id/{module_id}", status_code=status.HTTP_200_OK)
def update_post(module_id: str, updated_post: UpdatePost, db: Session = Depends(get_db)):
    result = db.query(PostDB).filter(PostDB.module_id == module_id).update(updated_post.model_dump())
    db.commit()

    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="post not found")

    return {"message": "Post updated successful"}

#update specific post by module id & user id
@app.put("/api/update-specific-post/module/{module_id}/{id}", status_code=status.HTTP_200_OK)
def update_specific_module_post(module_id: str, id:int, updated_post: UpdatePost, db: Session = Depends(get_db)):
    post = db.query(PostDB).filter(
        PostDB.module_id == module_id,
        PostDB.id == id).update(updated_post.model_dump())
    db.commit()

    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="post not found")

    return {"message": "Post updated successful"}


#delete post by module id
@app.delete("/api/delete-post-by-module-id/{module_id}", status_code=status.HTTP_200_OK)
def delete_post(module_id: str, db: Session = Depends(get_db)):
    post = db.query(PostDB).filter(PostDB.module_id == module_id).first()
    db.delete(post)
    db.commit()

    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

    return {"message": "Deleted Post"}

#delete specific post by id & module id
@app.delete("/api/delete-specific-post/module/{module_id}/{id}", status_code=status.HTTP_200_OK)
def delete_specific_post(module_id: str, id:int, db: Session = Depends(get_db)):
    post = db.query(PostDB).filter(
        PostDB.module_id == module_id,
        PostDB.id == id).first()
    db.delete(post)
    db.commit()

    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

    return {"message": "Deleted Post"}


#------------- Likes -------------#
#using like table in db to get all likes
@app.get("/api/get-all-likes", response_model=list[Like])
def get_likes(db: Session = Depends(get_db)):
    stmt = select(LikeDB).order_by(LikeDB.id)
    return list(db.execute(stmt).scalars())

#Add like to a post as a user
@app.post("/api/add-like/{user_id}/{id}", response_model=Like, status_code=status.HTTP_201_CREATED)
def like_post(payload: AddLike, db: Session = Depends(get_db)):
    like = LikeDB(**payload.model_dump())
    db.add(like)

    commit_or_rollback(db, "Post could not be Liked")
    return like

#Remove like to a post as a user
@app.delete("/api/remove-like/{user_id}/{id}", status_code=status.HTTP_200_OK)
def remove_like(user_id: int, id:int, db: Session = Depends(get_db)):
    like = db.query(LikeDB).filter(
        LikeDB.user_id == user_id,
        LikeDB.id == id,
        ).first()
    db.delete(like)
    db.commit()

    if not like:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

    return {"message": "removed like"}

#------------- Comments -------------#
#get all comments
@app.get("/api/get-all-comments", response_model=list[Comment])
def get_comments(db: Session = Depends(get_db)):
    stmt = select(CommentDB).order_by(CommentDB.id)
    return list(db.execute(stmt).scalars())

#get all comments under a specific post
@app.get("/api/comments-by-post/{post_id}", response_model=list[Comment])
def get_comments_by_post(post_id: str, db: Session = Depends(get_db)):
    comments = db.query(CommentDB).filter(CommentDB.post_id == post_id).all()
    if not comments: 
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found") #if not found return 404
    return comments

#get all comments by a user
@app.get("/api/comments-by-user/{user_id}", response_model=list[Comment])
def get_comments_by_user(user_id: str, db: Session = Depends(get_db)):
    comments = db.query(CommentDB).filter(CommentDB.user_id == user_id).all()
    if not comments: 
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found") #if not found return 404
    return comments

#Add Comment to a post
@app.post("/api/add-comment", response_model=AddComment, status_code=status.HTTP_201_CREATED)
def add_comment(payload: AddComment, db: Session = Depends(get_db)):
    comment = CommentDB(**payload.model_dump())
    db.add(comment)

    commit_or_rollback(db, "Could not comment ")
    return comment

#Remove comment to a post as a user
@app.delete("/api/remove-comment/{id}", status_code=status.HTTP_200_OK)
def remove_comment(id:int, db: Session = Depends(get_db)):
    comment = db.query(CommentDB).filter(
        CommentDB.id == id,
        ).first()
    db.delete(comment)
    db.commit()

    if not comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")

    return {"message": "removed comment"}


@app.put("/api/comments/{id}", status_code=status.HTTP_200_OK)
def update_comment(id: int, payload: AddComment, db: Session = Depends(get_db)):
    """Update a comment's content"""
    comment = db.get(CommentDB, id)
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")

    # Allow updating only the content (and optionally user_id/post_id if needed)
    for key, value in payload.model_dump().items():
        setattr(comment, key, value)
    db.commit()
    db.refresh(comment)
    return {"message": "Comment updated successfully"}