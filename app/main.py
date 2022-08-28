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


# Connecting to the database
while True:
    try:
        myDb = mysql.connector.connect(
            host="localhost",
            user="dasun",
            password=os.environ.get("DB_PASS"),
            database=os.environ.get("DB_DB")
        )
        cursor = myDb.cursor()
        print("Database connection was successfull!")
        break
    except Exception as error:
        print("Connecting to database failed!")
        print("Error", error)
        time.sleep(2)


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
async def update_post(id: int, post: PostsUpdate, response: Response):
    cursor.execute(""" UPDATE post SET  title = %s, content = %s WHERE id = %s """,
                   (post.title, post.content, str(id)))
    myDb.commit()
    return {
        "status": f"{cursor.rowcount} updated"
    }


@app.delete("/posts/{id}")
async def delete_post(id: int, db: Session = Depends(get_db)):
    post = db.query(models.Post).filter(models.Post.id == id)

    if not post:
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


def responseGen(cursor, type):
    columns = [i[0] for i in cursor.description]
    data = None

    match type:
        case "ALL":
            data = cursor.fetchall()
        case "ONE":
            data = cursor.fetchone()

    response = []
    for i in data:
        child_res = {}
        for index, item in enumerate(i):
            child_res[columns[index]] = item
        response.append(child_res)

    return response
