# Python FastAPI 개념 정리

FastAPI는 Python으로 작성된 **현대적인 고성능 웹 프레임워크**입니다.
Python 타입 힌트를 기반으로 자동 유효성 검사, 자동 문서 생성, 비동기 처리를 지원합니다.

---

## 목차

1. [FastAPI 소개](#1-fastapi-소개)
2. [설치 및 환경 설정](#2-설치-및-환경-설정)
3. [최소 실행 예제](#3-최소-실행-예제)
4. [라우팅 (Routing)](#4-라우팅-routing)
5. [HTTP 메서드](#5-http-메서드)
6. [요청 객체 (Request)](#6-요청-객체-request)
7. [응답 객체 (Response)](#7-응답-객체-response)
8. [APIRouter — 라우트 모듈화](#8-apirouter--라우트-모듈화)
9. [에러 핸들링](#9-에러-핸들링)
10. [미들웨어 (Middleware)](#10-미들웨어-middleware)
11. [의존성 주입 (Dependency Injection)](#11-의존성-주입-dependency-injection)
12. [데이터베이스 연동 — SQLite](#12-데이터베이스-연동--sqlite)
13. [JWT 인증 (python-jose)](#13-jwt-인증-python-jose)
14. [환경 변수 & 설정 관리](#14-환경-변수--설정-관리)
15. [애플리케이션 수명 주기 (lifespan)](#15-애플리케이션-수명-주기-lifespan)
16. [FastAPI vs Flask vs Django 비교](#16-fastapi-vs-flask-vs-django-비교)

---

## 1. FastAPI 소개

### 특징

| 항목 | 설명 |
|------|------|
| **고성능** | Starlette(ASGI) + Pydantic 기반. Node.js, Go 수준의 성능 |
| **타입 힌트 기반** | Python 타입 힌트로 요청/응답 유효성 검사 자동 처리 |
| **자동 문서 생성** | Swagger UI(`/docs`), ReDoc(`/redoc`) 자동 생성 |
| **비동기 지원** | `async/await` 네이티브 지원 (ASGI 기반) |
| **Pydantic 통합** | 요청 데이터 파싱·검증·직렬화를 Pydantic 모델로 처리 |

### Flask/Django와의 핵심 차이

```
Flask   → 마이크로 프레임워크. 최소 기능만 제공. WSGI 기반.
Django  → 풀스택 프레임워크. ORM·Admin·Auth 등 배터리 포함. WSGI/ASGI.
FastAPI → 현대적 API 프레임워크. 타입 힌트 + 자동 문서 + 비동기. ASGI 기반.
```

---

## 2. 설치 및 환경 설정

### 가상 환경 생성 (권장)

```bash
# 가상 환경 생성
python -m venv venv

# 활성화 (macOS / Linux)
source venv/bin/activate

# 활성화 (Windows)
venv\Scripts\activate

# 비활성화
deactivate
```

### FastAPI 설치

```bash
pip install fastapi

# ASGI 서버 (개발용)
pip install "uvicorn[standard]"

# requirements.txt로 의존성 관리
pip freeze > requirements.txt
pip install -r requirements.txt
```

---

## 3. 최소 실행 예제

```python
# main.py
from fastapi import FastAPI

# FastAPI 앱 인스턴스 생성
app = FastAPI()


@app.get("/")            # GET "/" 에 함수를 연결 (라우팅)
async def index():
    return {"message": "Hello, FastAPI!"}  # dict 반환 → 자동으로 JSON 응답
```

### 실행

```bash
# 방법 1: uvicorn CLI (권장)
uvicorn main:app --reload

# 방법 2: 직접 실행
# main.py 내부에 아래 코드 추가 후
import uvicorn
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

python main.py
```

서버 기본 주소: `http://127.0.0.1:8000`
자동 문서: `http://127.0.0.1:8000/docs`

---

## 4. 라우팅 (Routing)

HTTP 메서드 이름을 그대로 데코레이터로 사용합니다.

### 기본 라우팅

```python
@app.get("/")
async def index():
    return {"message": "메인 페이지"}

@app.get("/about")
async def about():
    return {"message": "소개 페이지"}
```

### 경로 파라미터 (Path Parameters)

URL의 일부를 변수로 받습니다. Flask의 `<int:id>`에 해당합니다.

```python
# {변수명} : 기본값은 str
@app.get("/user/{username}")
async def get_user(username: str):
    return {"username": username}

# 타입 힌트로 자동 변환 및 유효성 검사
@app.get("/post/{post_id}")
async def get_post(post_id: int):   # int로 자동 변환, 정수가 아니면 422 오류
    return {"post_id": post_id}
```

### 쿼리 파라미터 (Query Parameters)

함수 파라미터에 기본값을 주면 쿼리 파라미터로 인식합니다.

```python
# GET /items?page=1&limit=10
@app.get("/items")
async def get_items(page: int = 1, limit: int = 10):
    return {"page": page, "limit": limit}

# Optional 쿼리 파라미터
from typing import Optional

@app.get("/search")
async def search(keyword: Optional[str] = None):
    return {"keyword": keyword}
```

---

## 5. HTTP 메서드

각 HTTP 메서드에 대응하는 데코레이터를 사용합니다.

```python
@app.get("/items")          # 조회
@app.post("/items")         # 생성
@app.put("/items/{id}")     # 전체 수정
@app.patch("/items/{id}")   # 부분 수정
@app.delete("/items/{id}")  # 삭제
```

### REST API 메서드 용도 정리

| 메서드 | 용도 | 예시 |
|--------|------|------|
| `GET` | 리소스 조회 | 목록 조회, 상세 조회 |
| `POST` | 리소스 생성 | 회원가입, 게시글 작성 |
| `PUT` | 리소스 전체 수정 | 프로필 전체 교체 |
| `PATCH` | 리소스 부분 수정 | 닉네임만 변경 |
| `DELETE` | 리소스 삭제 | 계정 삭제 |

---

## 6. 요청 객체 (Request)

### Pydantic 모델로 요청 바디 받기 (권장)

타입 힌트 기반으로 자동 유효성 검사가 이루어집니다.

```python
from pydantic import BaseModel
from typing import Optional

# 요청 바디 스키마 정의
class UserCreate(BaseModel):
    email:    str
    password: str
    name:     str
    phone:    Optional[str] = None  # Optional: 선택 필드

@app.post("/users")
async def create_user(body: UserCreate):
    # body.email, body.password 등으로 접근
    return {"email": body.email, "name": body.name}
```

### dict로 받기 (유연한 처리가 필요할 때)

```python
@app.post("/flexible")
async def flexible(body: dict):
    email = body.get("email")
    return {"received": body}
```

### 헤더 받기

```python
from fastapi import Header
from typing import Optional

@app.get("/header-example")
async def header_example(authorization: Optional[str] = Header(None)):
    return {"auth": authorization}
```

### 쿼리 파라미터 + 경로 파라미터 혼합

```python
@app.get("/users/{user_id}/posts")
async def get_user_posts(
    user_id: int,              # 경로 파라미터
    page: int = 1,             # 쿼리 파라미터
    limit: int = 10,           # 쿼리 파라미터
):
    return {"user_id": user_id, "page": page, "limit": limit}
```

---

## 7. 응답 객체 (Response)

### dict/list 반환 (가장 단순)

```python
@app.get("/")
async def index():
    return {"message": "Hello"}     # 자동으로 JSON 응답, 200 OK
```

### JSONResponse로 상태 코드 지정

```python
from fastapi.responses import JSONResponse

@app.post("/users")
async def create_user(body: dict):
    return JSONResponse(
        status_code=201,
        content={"success": True, "message": "생성 완료"}
    )
```

### 응답 모델 (Response Model)

응답 스키마를 정의하여 자동 직렬화 및 문서화합니다.

```python
from pydantic import BaseModel

class UserResponse(BaseModel):
    id:    int
    email: str
    name:  str

# response_model 지정 시 자동으로 해당 필드만 반환 (password_hash 등 제외)
@app.get("/users/{user_id}", response_model=UserResponse)
async def get_user(user_id: int):
    return {"id": user_id, "email": "user@example.com", "name": "홍길동"}
```

---

## 8. APIRouter — 라우트 모듈화

Flask의 `Blueprint`에 해당합니다. 라우트를 기능별로 파일을 나눠 관리합니다.

### 구조 예시

```
project/
├── main.py
└── routes/
    ├── __init__.py
    ├── auth.py      # 인증 관련 라우트
    └── user.py      # 사용자 관련 라우트
```

### APIRouter 생성 (routes/auth.py)

```python
from fastapi import APIRouter
from fastapi.responses import JSONResponse

# APIRouter 생성
router = APIRouter()


@router.post("/login")
async def login(body: dict):
    return JSONResponse(content={"message": "로그인 성공"})


@router.post("/register")
async def register(body: dict):
    return JSONResponse(status_code=201, content={"message": "회원가입 성공"})
```

### APIRouter 등록 (main.py)

```python
from fastapi import FastAPI
from routes.auth import router as auth_router
from routes.user import router as user_router

app = FastAPI()

# prefix: 라우터의 모든 경로 앞에 공통 URL 접두사 추가
app.include_router(auth_router, prefix="/api/auth")
app.include_router(user_router, prefix="/api/user")

# 결과:
# auth_router의 /login    → /api/auth/login
# auth_router의 /register → /api/auth/register
# user_router의 /me       → /api/user/me
```

---

## 9. 에러 핸들링

### HTTPException

```python
from fastapi import HTTPException

@app.get("/users/{user_id}")
async def get_user(user_id: int):
    if user_id <= 0:
        # detail: 클라이언트에게 전달될 오류 메시지
        raise HTTPException(status_code=400, detail="유효하지 않은 사용자 ID입니다.")

    user = find_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다.")

    return user
```

### 전역 예외 핸들러

Flask의 `@app.errorhandler()`에 해당합니다.

```python
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

app = FastAPI()


@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    return JSONResponse(
        status_code=404,
        content={"success": False, "message": "요청한 리소스를 찾을 수 없습니다."}
    )


@app.exception_handler(500)
async def internal_error_handler(request: Request, exc):
    return JSONResponse(
        status_code=500,
        content={"success": False, "message": "서버 내부 오류가 발생했습니다."}
    )


# 커스텀 예외 클래스도 처리 가능
class AuthError(Exception):
    def __init__(self, message: str):
        self.message = message

@app.exception_handler(AuthError)
async def auth_error_handler(request: Request, exc: AuthError):
    return JSONResponse(
        status_code=401,
        content={"success": False, "message": exc.message}
    )
```

---

## 10. 미들웨어 (Middleware)

모든 요청/응답에 공통 로직을 적용합니다. Flask의 `before_request` / `after_request`에 해당합니다.

```python
from fastapi import FastAPI, Request
import time

app = FastAPI()


@app.middleware("http")
async def logging_middleware(request: Request, call_next):
    """
    모든 요청에 실행되는 미들웨어.
    1. 요청 전처리 (로깅, 인증 등)
    2. call_next(request) : 다음 처리 단계(라우트 함수)로 전달
    3. 응답 후처리 (헤더 추가 등)
    """
    start_time = time.time()

    # ── 요청 전처리 ──────────────────────────────
    print(f"[요청] {request.method} {request.url.path}")

    # 다음 처리 단계로 요청 전달 (라우트 함수 실행)
    response = await call_next(request)

    # ── 응답 후처리 ──────────────────────────────
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)

    return response


# CORS 미들웨어 추가
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],        # 허용할 오리진 (운영: 특정 도메인만)
    allow_methods=["*"],        # 허용할 HTTP 메서드
    allow_headers=["*"],        # 허용할 헤더
)
```

---

## 11. 의존성 주입 (Dependency Injection)

FastAPI의 핵심 기능입니다. `Depends()`를 사용해 공통 로직을 재사용합니다.
Flask의 `@before_request`나 커스텀 데코레이터보다 더 명시적이고 테스트하기 쉽습니다.

```python
from fastapi import Depends, Header, HTTPException


# ─── 의존성 함수 정의 ────────────────────────
def get_current_user(authorization: str = Header(...)):
    """
    Authorization 헤더에서 토큰을 추출하고 검증합니다.
    이 함수를 Depends()로 주입받은 라우트는
    자동으로 JWT 인증이 처리됩니다.
    """
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="인증 토큰이 필요합니다.")

    token = authorization.split(" ")[1]
    user_id = verify_jwt_token(token)  # 토큰 검증 로직

    if not user_id:
        raise HTTPException(status_code=401, detail="유효하지 않은 토큰입니다.")

    return user_id


# ─── 의존성 사용 ─────────────────────────────
@app.get("/profile")
async def get_profile(user_id: str = Depends(get_current_user)):
    # get_current_user()의 반환값이 user_id에 주입됩니다
    return {"user_id": user_id}


# 중첩 의존성도 가능
def get_db_connection():
    conn = create_connection()
    try:
        yield conn  # yield 사용 시 finally로 정리 보장
    finally:
        conn.close()

@app.get("/users")
async def get_users(
    user_id: str = Depends(get_current_user),  # 인증
    db = Depends(get_db_connection),            # DB 연결
):
    return db.execute("SELECT * FROM users").fetchall()
```

---

## 12. 데이터베이스 연동 — SQLite

Python 내장 `sqlite3` 모듈을 사용합니다. Flask와 동일한 방식입니다.

```python
import sqlite3
from config import Config


def get_db() -> sqlite3.Connection:
    """
    SQLite 데이터베이스 연결을 생성하여 반환합니다.
    row_factory 설정으로 컬럼명 접근이 가능합니다.
    """
    conn = sqlite3.connect(Config.DATABASE_PATH)
    conn.row_factory = sqlite3.Row  # dict처럼 컬럼명으로 접근 가능
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


# ── 라우트에서 사용 예시 ─────────────────────
@app.get("/users")
async def get_users():
    conn = get_db()
    try:
        users = conn.execute("SELECT id, email, name FROM users").fetchall()
        return [dict(u) for u in users]  # sqlite3.Row → dict 변환
    finally:
        conn.close()
```

---

## 13. JWT 인증 (python-jose)

```bash
pip install "python-jose[cryptography]"
pip install "passlib[bcrypt]"
```

### 토큰 생성

```python
import uuid
from datetime import datetime, timedelta, timezone
from jose import jwt

SECRET_KEY = "your-secret-key"
ALGORITHM  = "HS256"


def create_access_token(user_id: str) -> str:
    """액세스 토큰 생성 (유효기간 1시간)"""
    expire = datetime.now(timezone.utc) + timedelta(hours=1)

    payload = {
        "sub":  user_id,
        "type": "access",
        "jti":  str(uuid.uuid4()),  # 블랙리스트 처리용 고유 ID
        "exp":  expire,
    }

    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
```

### 토큰 검증

```python
from jose import JWTError, jwt


def verify_token(token: str) -> dict | None:
    """JWT 토큰 검증. 성공 시 payload, 실패 시 None 반환"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None
```

### 비밀번호 해시 (passlib)

```python
from passlib.context import CryptContext

# bcrypt 알고리즘 사용
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# 해시화
password_hash = pwd_context.hash("MyPassword1!")

# 검증
is_valid = pwd_context.verify("MyPassword1!", password_hash)  # True
```

### JWT 동작 흐름

```
클라이언트                         서버
    │                               │
    │  POST /api/auth/login         │
    │ ─────────────────────────────>│
    │                               │  토큰 생성
    │  access_token + refresh_token │
    │ <─────────────────────────────│
    │                               │
    │  GET /api/user/me             │
    │  Authorization: Bearer <AT>   │
    │ ─────────────────────────────>│  토큰 검증 (Depends)
    │  응답 데이터                   │
    │ <─────────────────────────────│
    │                               │
    │  (액세스 토큰 만료)             │
    │  POST /api/auth/refresh       │
    │  Authorization: Bearer <RT>   │
    │ ─────────────────────────────>│  리프레시 토큰 검증
    │  새로운 access_token           │
    │ <─────────────────────────────│
```

---

## 14. 환경 변수 & 설정 관리

### 클래스 기반 설정 (권장)

```python
# config.py
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


class Config:
    SECRET_KEY:                      str = os.environ.get("SECRET_KEY", "dev-secret-key")
    JWT_SECRET_KEY:                  str = os.environ.get("JWT_SECRET_KEY", "dev-jwt-secret")
    JWT_ALGORITHM:                   str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    JWT_REFRESH_TOKEN_EXPIRE_MINUTES:int = 60 * 24 * 30
    DATABASE_PATH:                   str = os.path.join(BASE_DIR, "database.db")
    RESET_TOKEN_EXPIRES_MINUTES:     int = 30
    DEBUG:                          bool = os.environ.get("DEBUG", "true").lower() == "true"
```

```python
# main.py
from config import Config

app = FastAPI()
# Config.JWT_SECRET_KEY 등으로 사용
```

### .env 파일 사용 (python-dotenv)

```bash
pip install python-dotenv
```

```ini
# .env 파일
SECRET_KEY=my-super-secret-key
JWT_SECRET_KEY=my-jwt-secret-key
DEBUG=true
```

```python
from dotenv import load_dotenv
import os

load_dotenv()
secret_key = os.environ.get("SECRET_KEY")
```

---

## 15. 애플리케이션 수명 주기 (lifespan)

앱 시작/종료 시 실행할 코드를 정의합니다. Flask의 `@app.before_first_request`에 해당합니다.

```python
from contextlib import asynccontextmanager
from fastapi import FastAPI


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    앱 시작과 종료 시 실행되는 수명 주기 이벤트.
    yield 이전: 앱 시작 시 실행 (DB 초기화, 캐시 로드 등)
    yield 이후: 앱 종료 시 실행 (리소스 정리 등)
    """
    # ── 시작 시 ──────────────────────────────────
    print("앱 시작: DB 초기화")
    init_db()

    yield  # 여기서 앱이 실행됩니다

    # ── 종료 시 ──────────────────────────────────
    print("앱 종료: 리소스 정리")


# lifespan을 FastAPI 생성자에 전달
app = FastAPI(lifespan=lifespan)
```

---

## 16. FastAPI vs Flask vs Django 비교

| 항목 | FastAPI | Flask | Django |
|------|---------|-------|--------|
| **규모** | 마이크로~중규모 API | 마이크로 | 풀스택 |
| **서버 타입** | ASGI (비동기 지원) | WSGI (동기) | WSGI/ASGI |
| **ORM** | 없음 (SQLAlchemy 등 선택) | 없음 | 내장 ORM |
| **자동 문서** | 자동 생성 (Swagger, ReDoc) | 없음 | 없음 |
| **유효성 검사** | Pydantic 자동 처리 | 없음 (수동 또는 WTForms) | 내장 Forms |
| **타입 힌트** | 핵심 기능 | 선택적 | 선택적 |
| **비동기** | 네이티브 지원 | 제한적 | 제한적 |
| **인증** | 없음 (직접 구현) | 없음 (jwt 등 선택) | 내장 Auth |
| **관리자 페이지** | 없음 | 없음 | 내장 Admin |
| **학습 곡선** | 중간 (Pydantic, 비동기 개념) | 낮음 | 중간~높음 |
| **성능** | 매우 높음 | 보통 | 보통 |
| **적합한 사용** | REST API, 마이크로서비스, 고성능 서비스 | 소규모 API, 프로토타이핑 | 대규모 웹 서비스, 어드민 필요 시 |

### 선택 기준

```
FastAPI 선택 → 고성능 REST API, 타입 안전성 중요, 자동 문서 필요, 비동기 처리 필요
Flask   선택 → 빠른 프로토타이핑, 소규모 API, 가볍고 자유로운 구조
Django  선택 → 어드민 페이지 필요, 복잡한 ORM, 대규모 웹 서비스, 배터리 포함 선호
```

---

## 참고 자료

| 자료 | 링크 |
|------|------|
| FastAPI 공식 문서 | https://fastapi.tiangolo.com |
| Pydantic 문서 | https://docs.pydantic.dev |
| Uvicorn 문서 | https://www.uvicorn.org |
| python-jose 문서 | https://python-jose.readthedocs.io |
| passlib 문서 | https://passlib.readthedocs.io |

---

## 학습 순서 요약

```
FastAPI 설치 및 최소 실행
    ↓
라우팅 + 경로/쿼리 파라미터
    ↓
Pydantic 모델로 요청/응답 처리
    ↓
APIRouter로 라우트 분리
    ↓
에러 핸들링 + 미들웨어
    ↓
의존성 주입 (Depends)
    ↓
SQLite 데이터베이스 연동
    ↓
JWT 인증 구현 (python-jose + passlib)
    ↓
환경 변수 & 설정 관리
    ↓
애플리케이션 수명 주기 (lifespan)
```

> 📁 실습 예제 코드는 `test/` 폴더를 참고하세요.
