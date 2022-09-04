from fastapi import APIRouter, HTTPException, Depends, status, Response
from ..database import get_db
from .. import models, schemas, utils, oauth
from sqlalchemy.orm import Session

router = APIRouter(tags=['Authentication'])


@router.post("/login")
async def login(user_credentials: schemas.Login, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(
        models.User.email == user_credentials.email).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Invalid Email")

    if not utils.verify(user_credentials.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Invalid Password")

    access_token = oauth.create_access_token(data={"user_id": user.id})
    return {"access_token": access_token, "token_type": 'bearer'}
