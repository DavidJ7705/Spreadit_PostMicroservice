# app/main.py
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException, status, Response
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine
from app.models import Base, PostDB
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, selectinload

from .database import engine, SessionLocal
from .schemas import Post, AddPost, UpdatePost, UserPosts

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


#----------- Need to get posts by module aswell