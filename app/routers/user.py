from fastapi import Depends, APIRouter, HTTPException, Response, status
from typing import List
from sqlalchemy.orm import Session

from ..database import get_db
from .. import models, schemas, utils

#tags - it groups the documentation according to the route
router = APIRouter(prefix="/users", tags=['Users'])


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.UserOut)
async def create_post(new_user: schemas.UserCreate, db: Session = Depends(get_db)):
    user = models.User(**new_user.dict())

    hash_pwd = utils.hash(user.password)
    user.password = hash_pwd

    db.add(user)
    db.commit()
    # It returns newly created user
    db.refresh(user)
    return user


@router.get("/{id}", response_model=schemas.UserOut)
async def get_user(id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == id).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"User with id {id} does not exist")

    return user
