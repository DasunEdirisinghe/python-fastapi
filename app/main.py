from faulthandler import disable
from turtle import pos
from typing import Optional
from fastapi import FastAPI, Response, status, HTTPException, Depends
from pydantic import BaseModel
from random import randrange
import time
import mysql.connector

from .database import engine, get_db
from . import models
from sqlalchemy.orm import Session

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# pydentic model used to validate request schemas


class Posts(BaseModel):
    title: str
    content: str


class PostsUpdate(BaseModel):
    title: Optional[str]
    content: Optional[str]


# Connecting to the database
while True:
    try:
        myDb = mysql.connector.connect(
            host="localhost",
            user="dasun",
            password="Dasun973#",
            database="fastapi"
        )
        cursor = myDb.cursor()
        print("Database connection was successfull!")
        break
    except Exception as error:
        print("Connecting to database failed!")
        print("Error", error)
        time.sleep(2)


@app.get('/test')
def test_post(db: Session = Depends(get_db)): 
    posts = db.query(models.Post).all()
    return {"status": posts}


@app.get("/")
async def root():
    return {"msg": "success"}


@app.get("/posts")
async def posts(db: Session = Depends(get_db)):
    posts = db.query(models.Post).all()
    return {"data": posts}


@app.post("/createpost", status_code=status.HTTP_201_CREATED)
async def create_post(new_post: Posts):
    cursor.execute(""" INSERT INTO post (title, content) VALUES (%s, %s) """,
                   (new_post.title, new_post.content))
    myDb.commit()

    return {
        "status": "{count} rows affected".format(count=cursor.rowcount),
        "data": cursor.lastrowid
    }


@app.put("/posts/{id}")
async def update_post(id: int, post: PostsUpdate, response: Response):
    cursor.execute(""" UPDATE post SET  title = %s, content = %s WHERE id = %s """,
                   (post.title, post.content, str(id)))
    myDb.commit()
    return {
        "status": f"{cursor.rowcount} updated"
    }


@app.delete("/posts/{id}")
async def delete_post(id: int, response: Response):
    cursor.execute(""" DELETE FROM post WHERE id = %s """, (str(id),))
    print(cursor)
    myDb.commit()
    return {
        "status": f"{cursor.rowcount} deleted",
    }


# id is a path parameter
@app.get("/posts/{id}")
async def get_post(id: int, response: Response):
    cursor.execute(""" SELECT * FROM post WHERE id = %s """, (str(id),))
    post = responseGen(cursor=cursor, type='ALL')

    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"The id , {id} you are looking for does not exist")

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
