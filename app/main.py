
from fastapi import Depends, FastAPI, HTTPException, Response, status
from sqlalchemy.orm import Session
from typing import List

from . import models, schemas
from .database import engine, get_db

#Execute sqlalchemy models
models.Base.metadata.create_all(bind=engine)

app = FastAPI()


@app.get("/")
async def root():
    return {"msg": "success"}


@app.get("/posts", response_model=List[schemas.Posts])
async def posts(db: Session = Depends(get_db)):
    posts = db.query(models.Post).all()
    return posts


@app.post("/createpost", status_code=status.HTTP_201_CREATED, response_model=schemas.Posts)
async def create_post(new_post: schemas.BasePost, db: Session = Depends(get_db)):
    # post = models.Post(title=new_post.title,content=new_post.content, published=new_post.published)
    post = models.Post(**new_post.dict())
    db.add(post)
    db.commit()
    #It returns newly created post
    db.refresh(post)
    return post


@app.put("/posts/{id}")
async def update_post(id: int, updated_post: schemas.PostsUpdate, db: Session = Depends(get_db)):
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
