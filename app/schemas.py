from typing import Optional
from pydantic import BaseModel, EmailStr
from datetime import datetime


# pydentic model used to validate request schemas
class BasePost(BaseModel):
    title: str
    content: str
    published: Optional[bool]

    class Config:
        orm_mode = True


# Pydentic model for updating a post
class PostsUpdate(BaseModel):
    title: Optional[str]
    content: Optional[str]


class Posts(BasePost):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True


class DeletePost():
    id: int


class UserCreate(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: int
    email: EmailStr

    class Config:
        orm_mode = True
