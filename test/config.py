"""
config.py
─────────────────────────────────────────
FastAPI 애플리케이션 전역 설정을 관리하는 모듈.
환경 변수를 통해 운영/개발 환경을 분리할 수 있습니다.
"""

import os

# ─── 프로젝트 루트 경로 ─────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))


class Config:
    # ─── 애플리케이션 기본 설정 ──────────────────
    # 운영 환경에서는 반드시 환경 변수로 교체해야 합니다
    SECRET_KEY: str = os.environ.get("SECRET_KEY", "mango-fastapi-secret-key-change-in-production")

    # ─── JWT 설정 ────────────────────────────────
    # JWT 토큰 서명에 사용되는 비밀 키
    JWT_SECRET_KEY: str = os.environ.get("JWT_SECRET_KEY", "mango-jwt-secret-key-change-in-production")

    # JWT 서명 알고리즘 (HMAC-SHA256)
    JWT_ALGORITHM: str = "HS256"

    # 액세스 토큰 유효 기간: 60분
    # 만료 후 리프레시 토큰으로 재발급 받아야 합니다
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # 리프레시 토큰 유효 기간: 30일 (분 단위로 저장)
    # 이 기간이 지나면 재로그인이 필요합니다
    JWT_REFRESH_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 30

    # ─── SQLite 데이터베이스 설정 ─────────────────
    # 프로젝트 루트에 database.db 파일 생성
    DATABASE_PATH: str = os.path.join(BASE_DIR, "database.db")

    # ─── 비밀번호 재설정 토큰 설정 ───────────────
    # 비밀번호 재설정 토큰 유효 기간: 30분
    RESET_TOKEN_EXPIRES_MINUTES: int = 30

    # ─── 디버그 설정 ─────────────────────────────
    DEBUG: bool = os.environ.get("DEBUG", "true").lower() == "true"
