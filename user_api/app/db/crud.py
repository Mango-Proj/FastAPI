# app/db/crud.py
from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserCreate

# 사용자 이메일로 조회
def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

# 새 사용자 생성
def create_user(db: Session, user: UserCreate, hashed_password: str):
    db_user = User(
        email=user.email, 
        hashed_password=hashed_password,
        nickname=user.nickname
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user