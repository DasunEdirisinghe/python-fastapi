from faulthandler import disable
import os
from turtle import pos, title
from typing import Optional
from fastapi import FastAPI, Response, status, HTTPException, Depends
from pydantic import BaseModel
from random import randrange
import time
import mysql.connector
import os

from .database import engine, get_db
from . import models
from sqlalchemy.orm import Session

#Execute sqlalchemy models
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# pydentic model used to validate request schemas
class Posts(BaseModel):
    title: str
    content: str
    published: Optional[bool]

#Pydentic model for updating a post
class PostsUpdate(BaseModel):
    title: Optional[str]
    content: Optional[str]


@app.get("/")
async def root():
    return {"msg": "success"}


@app.get("/posts")
async def posts(db: Session = Depends(get_db)):
    posts = db.query(models.Post).all()
    return {"data": posts}


@app.post("/createpost", status_code=status.HTTP_201_CREATED)
async def create_post(new_post: Posts, db: Session = Depends(get_db)):
    # post = models.Post(title=new_post.title,content=new_post.content, published=new_post.published)
    post = models.Post(**new_post.dict())
    db.add(post)
    db.commit()
    #It returns newly created post
    db.refresh(post)
    return {"data": post}


@app.put("/posts/{id}")
async def update_post(id: int, updated_post: PostsUpdate, db: Session = Depends(get_db)):
    post = db.query(models.Post).filter(models.Post.id == id)
    if not post.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with id {id} does not exist")

    result = {}
    #Removing all None valued keys
    for key, value in updated_post.dict().items():
        if value:
            result[key] = value

    post.update(result, synchronize_session=False)
    db.commit()
    return {"data": post.first()}


@app.delete("/posts/{id}")
async def delete_post(id: int, db: Session = Depends(get_db)):
    post = db.query(models.Post).filter(models.Post.id == id)
    if not post.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with id {id} does not exist")
    post.delete()
    #post.delete(synchronize_session=False) is much more efficient
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# id is a path parameter
@app.get("/posts/{id}")
async def get_post(id: int, db: Session = Depends(get_db)):
    #.all() for get all matching data
    #.first() is going to find the first matching data
    post = db.query(models.Post).filter(models.Post.id == id).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with id {id} does not exist")
    return {
        "data": post
    }