# app/schemas/user.py
from pydantic import BaseModel, EmailStr

# 입력 스키마: 회원가입 시 클라이언트로부터 받는 데이터
class UserCreate(BaseModel):
    email: EmailStr
    password: str
    nickname: str
    
# 출력 스키마: 클라이언트에게 응답할 때 보낼 데이터 (비밀번호 제외)
class UserInDB(BaseModel):
    id: int
    email: EmailStr
    nickname: str
    is_active: bool

    class Config:
        # Pydantic이 SQLAlchemy 객체를 다룰 수 있도록 설정
        from_attributes = True