"""
main.py
─────────────────────────────────────────
FastAPI 애플리케이션 진입점.

실행 방법:
    uvicorn main:app --reload

또는 직접 실행:
    python main.py

자동 API 문서:
    http://localhost:8000/docs      (Swagger UI)
    http://localhost:8000/redoc     (ReDoc)
"""

from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from config import Config
from database import init_db
from routes.auth import router as auth_router
from routes.user import router as user_router


# ─── 애플리케이션 수명 주기 ──────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    FastAPI 앱 시작/종료 시 실행되는 수명 주기 이벤트.
    - 시작 시: 데이터베이스 초기화 (테이블 생성)
    - 종료 시: 정리 작업 (현재는 없음)
    """
    # ── 앱 시작 시 ───────────────────────────────
    # 이미 테이블이 존재하면 건너뜁니다 (IF NOT EXISTS)
    init_db()
    yield
    # ── 앱 종료 시 ───────────────────────────────
    # 필요한 정리 작업이 있으면 여기에 추가합니다


# ─── FastAPI 앱 인스턴스 생성 ────────────────────
app = FastAPI(
    title="Mango FastAPI User API",
    description="FastAPI + SQLite 기반 사용자 계정 관리 REST API",
    version="1.0.0",
    lifespan=lifespan,
)


# ── 1. 라우터 등록 ───────────────────────────────
# 각 라우터 그룹에 URL prefix를 지정하여 등록합니다
app.include_router(auth_router, prefix="/api/auth")  # 인증 관련 API
app.include_router(user_router, prefix="/api/user")  # 계정 관리 API


# ── 2. 전역 예외 핸들러 ──────────────────────────
@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    """존재하지 않는 엔드포인트 요청 시"""
    return JSONResponse(
        status_code=404,
        content={"success": False, "message": "요청한 API를 찾을 수 없습니다."},
    )


@app.exception_handler(405)
async def method_not_allowed_handler(request: Request, exc):
    """허용되지 않은 HTTP 메서드 사용 시"""
    return JSONResponse(
        status_code=405,
        content={"success": False, "message": "허용되지 않은 요청 방식입니다."},
    )


@app.exception_handler(500)
async def internal_error_handler(request: Request, exc):
    """예상치 못한 서버 오류 발생 시"""
    return JSONResponse(
        status_code=500,
        content={"success": False, "message": "서버 내부 오류가 발생했습니다."},
    )


# ── 3. 헬스체크 엔드포인트 ───────────────────────
@app.get("/api/health")
async def health_check():
    """서버 상태 확인용 엔드포인트"""
    return JSONResponse(
        status_code=200,
        content={
            "success": True,
            "message": "서버가 정상 동작 중입니다.",
            "version": "1.0.0",
        },
    )


# ─── 개발 서버 실행 ──────────────────────────────
# python main.py 로 직접 실행할 때만 동작합니다
if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",          # 모든 네트워크 인터페이스에서 수신
        port=8000,                 # 포트 번호
        reload=Config.DEBUG,       # 개발 모드: 코드 변경 시 자동 재시작
    )
