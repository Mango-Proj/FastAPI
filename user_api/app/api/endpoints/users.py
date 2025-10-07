# app/api/endpoints/users.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db import crud
from app.schemas.user import UserCreate, UserInDB
from app.core.security import get_password_hash 

router = APIRouter(
    prefix="/users",
    tags=["users"]
)

@router.post("/", response_model=UserInDB)
def create_new_user(user: UserCreate, db: Session = Depends(get_db)):

    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
        

    hashed_password = get_password_hash(user.password)
    return crud.create_user(db=db, user=user, hashed_password=hashed_password)