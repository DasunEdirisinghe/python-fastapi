from fastapi import  FastAPI

from . import models, schemas, utils
from .database import engine
from .routers import post, user, auth

# Execute sqlalchemy models
models.Base.metadata.create_all(bind=engine)

app = FastAPI()
app.include_router(post.router)
app.include_router(user.router)
app.include_router(auth.router)


@app.get("/")
async def root():
    return {"msg": "success"}





