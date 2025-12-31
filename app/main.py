# app/main.py
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException, status, Response
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, SessionLocal
from app.models import Base, PostDB, LikeDB, CommentDB
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, selectinload
from .schemas import Post, AddPost, UpdatePost, Comment, AddComment, UpdateComment, UserPosts, Like, AddLike

import os
import aio_pika
import json
import asyncio

RABBIT_URL = os.getenv("RABBIT_URL")

async def publish_event(routing_key: str, data: dict):
    if not RABBIT_URL:
        return
        
    try:
        connection = await aio_pika.connect_robust(RABBIT_URL)
        async with connection:
            channel = await connection.channel()
            exchange = await channel.declare_exchange("events_topic", aio_pika.ExchangeType.TOPIC)
            
            message = aio_pika.Message(
                body=json.dumps(data).encode(),
                content_type="application/json"
            )
            await exchange.publish(message, routing_key=routing_key)
    except Exception as e:
        print(f"Failed to publish event {routing_key}: {e}")

async def process_user_deleted(data: dict):
    user_id = data.get("user_id")
    if not user_id:
        return
    
    print(f"Processing user deletion for user_id: {user_id}")
    db = SessionLocal()
    try:
        # 1. Delete user's posts
        posts = db.query(PostDB).filter(PostDB.user_id == user_id).all()
        for post in posts:
            db.delete(post)
        
        # 2. Delete user's likes
        likes = db.query(LikeDB).filter(LikeDB.user_id == user_id).all()
        for like in likes:
            db.delete(like)
            
        # 3. Delete user's comments
        comments = db.query(CommentDB).filter(CommentDB.user_id == user_id).all()
        for comment in comments:
            db.delete(comment)
            
        db.commit()
        print(f"Cleaned up data for user {user_id}")
    except Exception as e:
        print(f"Error processing user deletion: {e}")
        db.rollback()
    finally:
        db.close()

async def process_module_deleted(data: dict):
    module_id = data.get("module_id")
    if not module_id:
        return

    print(f"Processing module deletion for module_id: {module_id}")
    db = SessionLocal()
    try:
        # Delete all posts in this module
        posts = db.query(PostDB).filter(PostDB.module_id == module_id).all()
        for post in posts:
            db.delete(post)
            
        db.commit()
        print(f"Removed {len(posts)} posts for module {module_id}")
    except Exception as e:
        print(f"Error processing module deletion: {e}")
        db.rollback()
    finally:
        db.close()

async def consume_events():
    if not RABBIT_URL:
        print("RABBIT_URL not set, skipping consumer")
        return

    while True:
        try:
            connection = await aio_pika.connect_robust(RABBIT_URL)
            async with connection:
                channel = await connection.channel()
                
                await channel.declare_exchange("events_topic", aio_pika.ExchangeType.TOPIC)
                queue = await channel.declare_queue("post_service_queue", durable=True)
                
                # Bind to multiple keys
                await queue.bind("events_topic", routing_key="user.deleted")
                await queue.bind("events_topic", routing_key="module.deleted")
                
                print("Post Service Consumer Started")
                
                async with queue.iterator() as iterator:
                    async for message in iterator:
                        async with message.process():
                            data = json.loads(message.body)
                            if message.routing_key == "user.deleted":
                                await process_user_deleted(data)
                            elif message.routing_key == "module.deleted":
                                await process_module_deleted(data)
                                
        except asyncio.CancelledError:
            print("Consumer cancelled")
            break
        except Exception as e:
            print(f"Consumer connection lost: {e}, retrying in 5s...")
            await asyncio.sleep(5)

#Replacing @app.on_event("startup")
@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    task = asyncio.create_task(consume_events())
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
async def add_post(payload: AddPost, db: Session = Depends(get_db)):
    post = PostDB(**payload.model_dump())
    db.add(post)

    commit_or_rollback(db, "Post could not be created")
    db.refresh(post)
    await publish_event("post.created", {"post_id": post.id, "user_id": post.user_id})
    return post

#using db to get all posts
@app.get("/api/get-all-posts", response_model=list[Post], status_code=status.HTTP_200_OK)
def get_all_posts(db: Session = Depends(get_db)):
    stmt = select(PostDB).options(selectinload(PostDB.likes), selectinload(PostDB.comments)).order_by(PostDB.id)
    return list(db.execute(stmt).scalars())


#------------- Posts Backend Id based functions -------------#
#get post by its backend id  
@app.get("/api/post-by-id/{id}", response_model=Post, status_code=status.HTTP_200_OK)
def get_post(id: int, db: Session = Depends(get_db)):
    stmt = select(PostDB).options(selectinload(PostDB.likes), selectinload(PostDB.comments)).where(PostDB.id == id)
    post = db.execute(stmt).scalar_one_or_none()
    
    if not post: 
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found") #if not found return 404
    return post

#update post by backend id
@app.put("/api/update-post-by-id/{id}", status_code=status.HTTP_200_OK)
async def update_post(id: int, payload: UpdatePost, db: Session = Depends(get_db)):
    post = db.get(PostDB, id)
    if not post: 
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found") #if not found return 404
   
    for field, value in payload.model_dump().items():
        setattr(post, field, value)

    commit_or_rollback(db, "post update failed")
    db.refresh(post)
    
    await publish_event("post.updated", {"post_id": id, "updates": payload.model_dump()})

    return {"message": "Post updated successful"}
    
#delete post by backend id
@app.delete("/api/delete-post-by-id/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(id: int, db: Session = Depends(get_db)):
    post = db.get(PostDB, id)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found") #if not found return 404

    db.delete(post)
    db.commit()
    await publish_event("post.deleted", {"post_id": id})
    return Response(status_code = status.HTTP_204_NO_CONTENT)

#------------- Posts by User -------------#

#get posts by its user id  
@app.get("/api/post-by-user_id/{user_id}", response_model=list[UserPosts], status_code=status.HTTP_200_OK)
def get_post(user_id: int, db: Session = Depends(get_db)):
    posts = db.query(PostDB).filter(PostDB.user_id == user_id).all()
    if not posts: 
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Posts not found for user provided")
    
    return posts

#------------- Posts by Module -------------#

#get posts by its module id  
@app.get("/api/post-by-module_id/{module_id}", response_model=list[UserPosts], status_code=status.HTTP_200_OK)
def get_post(module_id: int, db: Session = Depends(get_db)):
    posts = db.query(PostDB).filter(PostDB.module_id == module_id).all()
    if not posts: 
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Posts not found for module id provided")
    return posts

#------------- Likes -------------#

@app.get("/api/likes", response_model=list[Like], status_code=status.HTTP_200_OK)
def get_all_likes(db: Session = Depends(get_db)):
    stmt = select(LikeDB).order_by(LikeDB.id)
    return list(db.execute(stmt).scalars())


@app.post("/api/likes", response_model=Like, status_code=status.HTTP_201_CREATED)
async def add_like(payload: AddLike, db: Session = Depends(get_db)):

    like = LikeDB(**payload.model_dump())
    db.add(like)
    commit_or_rollback(db, "User already liked this post")

    db.refresh(like)
    await publish_event("post.liked", {"post_id": like.post_id, "user_id": like.user_id})
    return like


@app.delete("/api/likes", status_code=status.HTTP_200_OK)
async def remove_like(user_id: int, post_id: int, db: Session = Depends(get_db)):

    like = (
        db.query(LikeDB)
        .filter(LikeDB.user_id == user_id, LikeDB.post_id == post_id)
        .first()
    )

    if not like:
        raise HTTPException(status_code=404, detail="Like not found")

    db.delete(like)
    commit_or_rollback(db, "Failed to remove like")

    await publish_event("post.unliked", {"post_id": post_id, "user_id": user_id})

    return {"message": "Like removed successfully"}



#------------- Comments -------------#

# Get all comments
@app.get("/api/comments", response_model=list[Comment], status_code=status.HTTP_200_OK)
def get_all_comments(db: Session = Depends(get_db)):
    stmt = select(CommentDB).order_by(CommentDB.id)
    return list(db.execute(stmt).scalars())


# Get comments for a post
@app.get("/api/comments/{post_id}", response_model=list[Comment], status_code=status.HTTP_200_OK)
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
@app.get("/api/comments-by-user/{user_id}", response_model=list[Comment], status_code=status.HTTP_200_OK)
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
@app.post("/api/comments", response_model=Comment, status_code=status.HTTP_201_CREATED)
async def add_comment(payload: AddComment, db: Session = Depends(get_db)):
    comment = CommentDB(**payload.model_dump())
    db.add(comment)

    commit_or_rollback(db, "Comment could not be created")
    db.refresh(comment)
    await publish_event("comment.created", {"comment_id": comment.id, "post_id": comment.post_id})
    return comment


# Update a comment (just content)
@app.put("/api/comments/{comment_id}", status_code=status.HTTP_200_OK)
async def update_comment(comment_id: int, payload: UpdateComment, db: Session = Depends(get_db)):
    comment = db.get(CommentDB, comment_id)

    if not comment:
        raise HTTPException(404, "Comment not found")

    for key, value in payload.model_dump().items():
        setattr(comment, key, value)

    commit_or_rollback(db, "Failed updating comment")
    db.refresh(comment)
    await publish_event("comment.updated", {"comment_id": comment_id})
    return {"message": "Comment updated successfully"}


# Delete a comment
@app.delete("/api/comments/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_comment(comment_id: int, db: Session = Depends(get_db)):
    comment = db.get(CommentDB, comment_id)
    if not comment:
        raise HTTPException(404, "Comment not found")

    db.delete(comment)
    commit_or_rollback(db, "Failed deleting comment")

    await publish_event("comment.deleted", {"comment_id": comment_id})

    return Response(status_code=status.HTTP_204_NO_CONTENT)
