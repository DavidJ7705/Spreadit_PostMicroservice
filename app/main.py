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
from .schemas import Post, AddPost, UpdatePost, UserPosts, Like, AddLike, Comment, AddComment, UpdateComment

#Replacing @app.on_event("startup")
@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)   
    yield

app = FastAPI(lifespan=lifespan)

# CORS (add this block)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # dev-friendly; tighten in prod
    allow_methods=["*"],
    allow_headers=["*"],
)

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
@app.post("/api/add-post", response_model=Post, status_code=status.HTTP_201_CREATED)
def add_post(payload: AddPost, db: Session = Depends(get_db)):
    post = PostDB(**payload.model_dump())
    db.add(post)

    commit_or_rollback(db, "Post could not be created")
    db.refresh(post)
    return post

#using db to get all posts
@app.get("/api/get-all-posts", response_model=list[Post])
def get_all_posts(db: Session = Depends(get_db)):
    stmt = select(PostDB).order_by(PostDB.id)
    return list(db.execute(stmt).scalars())


#------------- Posts Backend Id based functions -------------#
#get post by its backend id  
@app.get("/api/post-by-id/{id}", response_model=Post)
def get_post(id: int, db: Session = Depends(get_db)):
    post = db.get(PostDB, id)
    if not post: 
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found") #if not found return 404
    return post

#update post by backend id
@app.put("/api/update-post-by-id/{id}", status_code=status.HTTP_200_OK)
def update_post(id: int, payload: UpdatePost, db: Session = Depends(get_db)):
    post = db.get(PostDB, id)
    if not post: 
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found") #if not found return 404
   
    for field, value in payload.model_dump().items():
        setattr(post, field, value)

    commit_or_rollback(db, "post update failed")
    db.refresh(post)

    return {"message": "Post updated successful"}
    
#delete post by backend id
@app.delete("/api/delete-post-by-id/{id}", status_code=status.HTTP_200_OK)
def delete_post(id: int, db: Session = Depends(get_db)):
    post = db.get(PostDB, id)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found") #if not found return 404

    db.delete(post)
    db.commit()

    return {"message": "Deleted Post"}

#------------- Posts by User -------------#

#get posts by its user id  
@app.get("/api/post-by-user_id/{user_id}", response_model=list[UserPosts])
def get_post(user_id: int, db: Session = Depends(get_db)):
    posts = db.query(PostDB).filter(PostDB.user_id == user_id).all()
    if not posts: 
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Posts not found for user provided")
    
    return posts

#------------- Posts by Module -------------#

#get posts by its module id  
@app.get("/api/post-by-module_id/{module_id}", response_model=list[UserPosts])
def get_post(module_id: int, db: Session = Depends(get_db)):
    posts = db.query(PostDB).filter(PostDB.module_id == module_id).all()
    if not posts: 
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Posts not found for module id provided")
    return posts

#------------- Likes -------------#

@app.get("/api/likes", response_model=list[Like])
def get_all_likes(db: Session = Depends(get_db)):
    stmt = select(LikeDB).order_by(LikeDB.id)
    return list(db.execute(stmt).scalars())


@app.post("/api/likes", response_model=Like, status_code=status.HTTP_201_CREATED)
def add_like(payload: AddLike, db: Session = Depends(get_db)):

    like = LikeDB(**payload.model_dump())
    db.add(like)
    commit_or_rollback(db, "User already liked this post")

    db.refresh(like)
    return like


@app.delete("/api/likes", status_code=status.HTTP_200_OK)
def remove_like(user_id: int, post_id: int, db: Session = Depends(get_db)):

    like = (
        db.query(LikeDB)
        .filter(LikeDB.user_id == user_id, LikeDB.post_id == post_id)
        .first()
    )

    if not like:
        raise HTTPException(status_code=404, detail="Like not found")

    db.delete(like)
    commit_or_rollback(db, "Failed to remove like")

    return {"message": "Like removed successfully"}



#------------- Comments -------------#

# Get all comments
@app.get("/api/comments", response_model=list[Comment])
def get_all_comments(db: Session = Depends(get_db)):
    stmt = select(CommentDB).order_by(CommentDB.id)
    return list(db.execute(stmt).scalars())


# Get comments for a post
@app.get("/api/comments/{post_id}", response_model=list[Comment])
def get_comments_for_post(post_id: int, db: Session = Depends(get_db)):
    comments = (
        db.query(CommentDB)
        .filter(CommentDB.post_id == post_id)
        .order_by(CommentDB.id)
        .all()
    )

    if not comments:
        raise HTTPException(404, "No comments found for this post")

    return comments


# Get comments by a user
@app.get("/api/comments-by-user/{user_id}", response_model=list[Comment])
def get_comments_for_user(user_id: int, db: Session = Depends(get_db)):
    comments = (
        db.query(CommentDB)
        .filter(CommentDB.user_id == user_id)
        .order_by(CommentDB.id)
        .all()
    )

    if not comments:
        raise HTTPException(404, "No comments found for this user")

    return comments



# Add a comment
@app.post("/api/comments", response_model=Comment, status_code=201)
def add_comment(payload: AddComment, db: Session = Depends(get_db)):
    comment = CommentDB(**payload.model_dump())
    db.add(comment)

    commit_or_rollback(db, "Comment could not be created")
    db.refresh(comment)
    return comment


# Update a comment (just content)
@app.put("/api/comments/{comment_id}", status_code=200)
def update_comment(comment_id: int, payload: UpdateComment, db: Session = Depends(get_db)):
    comment = db.get(CommentDB, comment_id)

    if not comment:
        raise HTTPException(404, "Comment not found")

    for key, value in payload.model_dump().items():
        setattr(comment, key, value)

    commit_or_rollback(db, "Failed updating comment")
    db.refresh(comment)
    return {"message": "Comment updated successfully"}


# Delete a comment
@app.delete("/api/comments/{comment_id}", status_code=200)
def delete_comment(comment_id: int, db: Session = Depends(get_db)):
    comment = db.get(CommentDB, comment_id)
    if not comment:
        raise HTTPException(404, "Comment not found")

    db.delete(comment)
    commit_or_rollback(db, "Failed deleting comment")

    return {"message": "Comment deleted successfully"}
