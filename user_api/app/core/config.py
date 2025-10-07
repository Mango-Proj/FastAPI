# app/core/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # 환경 변수에서 가져옵니다 (예: .env 파일)
    PROJECT_NAME: str = "MyFastAPIServer"
    DATABASE_URL: str = "sqlite:///./local_app_db.db" 
    SECRET_KEY: str = "my-jwt-secret-key"
    ALGORITHM: str = "HS256"

    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings()