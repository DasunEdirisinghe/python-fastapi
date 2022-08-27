# Main.py without ORM
from faulthandler import disable
from turtle import pos
from typing import Optional
from fastapi import FastAPI, Response, status, HTTPException
from pydantic import BaseModel
from random import randrange
import time
import mysql.connector

app = FastAPI()

# pydentic model used to validate request schemas


class Posts(BaseModel):
    title: str
    content: str


class PostsUpdate(BaseModel):
    title: Optional[str]
    content: Optional[str]


# storing post data in a local variable
my_posts = [
    {
        "title": "Post1",
        "content": "Content for post1",
        "id": 1
    },
    {
        "title": "Post2",
        "content": "Content for post2",
        "id": 2
    }
]

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


@app.get("/")
async def root():
    return {"msg": "success"}


@app.get("/posts")
async def posts():
    cursor.execute(""" SELECT * FROM post """)
    return {"data": responseGen(cursor=cursor, type="ALL")}


@app.post("/createpost", status_code=status.HTTP_201_CREATED)
async def create_post(new_post: Posts):
    # coming request data going through Post pydentic model and the we can convert it to a dict
    # also pydentic model helps us to validate request da ta
    # modified_post = new_post.dict().copy()
    # modified_post.update({"id": get
    cursor.execute(""" INSERT INTO post (title, content) VALUES (%s, %s) """,
                   (new_post.title, new_post.content))
    myDb.commit()

    return {
        "status": "{count} rows affected".format(count=cursor.rowcount),
        "data": cursor.lastrowid
    }


@app.put("/posts/{id}")
async def update_post(id: int, post: PostsUpdate, response: Response):
    # index = getIndex(id, my_posts)

    # if index != None:
    #     for key, value in post.dict().items():
    #         my_posts[index][key] = value
    # else:
    #     raise HTTPException(
    #         status_code=status.HTTP_204_NO_CONTENT, detail="No data")
    # return {"data": my_posts[index]}
    cursor.execute(""" UPDATE post SET  title = %s, content = %s WHERE id = %s """,
                   (post.title, post.content, str(id)))
    myDb.commit()
    return {
        "status": f"{cursor.rowcount} updated"
    }


@app.delete("/posts/{id}")
async def delete_post(id: int, response: Response):
    # index = getIndex(id, my_posts)

    # if not index:
    #     # After raising the HTTPException it is not going to execute below return statement.
    #     raise HTTPException(status_code=status.HTTP_200_OK, detail=[])
    # return {"data": my_posts.pop(index)}
    cursor.execute(""" DELETE FROM post WHERE id = %s """, (str(id),))
    print(cursor)
    myDb.commit()
    return {
        "status": f"{cursor.rowcount} deleted",
    }


# id is a path parameter
@app.get("/posts/{id}")
async def get_post(id: int, response: Response):
    # requested_post = [post for post in my_posts if post['id'] == id]

    # if not requested_post:
    #     response.status_code = status.HTTP_404_NOT_FOUND
    #     return {"data": []}
    # else:
    #     return {"data": requested_post}

    # Better than abouse solution
    # if not requested_post:
    #     raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
    #                         detail="No matched id for the request")
    # return Response(status_code=status.HTTP_204_NO_CONTENT)
    cursor.execute(""" SELECT * FROM post WHERE id = %s """, (str(id),))
    post = responseGen(cursor=cursor, type='ALL')

    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"The id , {id} you are looking for does not exist")

    return {
        "data": post
    }


def getNextId():
    id = 0
    for i in my_posts:
        if i["id"] > id:
            id = i["id"]
    return (id + randrange(0, 1231231))


def getIndex(id, posts):
    for i, dic in enumerate(posts):
        if dic['id'] == id:
            return i


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
