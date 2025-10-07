# app/db/database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings

# DB 엔진 생성
engine = create_engine(
    settings.DATABASE_URL, connect_args={"check_same_thread": False} # SQLite 전용 설정
)

# 세션 관리자 생성
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 모든 모델의 기반 클래스
Base = declarative_base()

# 의존성 주입을 위한 제너레이터 함수
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()