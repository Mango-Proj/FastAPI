# Mango FastAPI User API

Python FastAPI + SQLite 기반의 사용자 계정 관리 REST API입니다.

---

## 기술 스택

| 항목 | 내용 |
|------|------|
| 언어 | Python 3.10+ |
| 프레임워크 | FastAPI 0.110+ |
| 데이터베이스 | SQLite 3 |
| 인증 방식 | JWT (Access Token + Refresh Token) |
| 비밀번호 해시 | passlib `bcrypt` |

---

## 프로젝트 구조

```
fastapi/test/
├── main.py                  # 애플리케이션 진입점 (lifespan, 라우터 등록)
├── config.py                # 전역 설정 (JWT 만료, DB 경로 등)
├── database.py              # SQLite 연결 및 테이블 초기화
├── store.py                 # 메모리 기반 JWT 블랙리스트 저장소
├── routes/
│   ├── __init__.py
│   ├── auth.py              # 인증 API (회원가입, 로그인 등)
│   └── user.py              # 계정 관리 API (조회, 수정, 탈퇴)
├── utils/
│   ├── __init__.py
│   ├── validators.py        # 입력값 유효성 검사 함수
│   └── jwt_utils.py         # JWT 토큰 생성/검증 유틸리티
├── database.db              # SQLite DB 파일 (최초 실행 시 자동 생성)
├── requirements.txt
└── README.md
```

---

## 설치 및 실행

### 1. 가상 환경 생성 및 활성화

```bash
python -m venv venv

# macOS / Linux
source venv/bin/activate

# Windows
venv\Scripts\activate
```

### 2. 패키지 설치

```bash
pip install -r requirements.txt
```

### 3. 서버 실행

```bash
# 방법 1: uvicorn CLI (권장)
uvicorn main:app --reload

# 방법 2: 직접 실행
python main.py
```

서버가 시작되면 `database.db` 파일이 자동 생성되고 테이블이 초기화됩니다.

| 주소 | 설명 |
|------|------|
| `http://localhost:8000` | 기본 서버 주소 |
| `http://localhost:8000/docs` | Swagger UI 자동 문서 |
| `http://localhost:8000/redoc` | ReDoc 자동 문서 |

---

## 데이터베이스 스키마

### users 테이블

| 컬럼 | 타입 | 설명 |
|------|------|------|
| `id` | INTEGER PK | 자동 증가 고유 번호 |
| `email` | TEXT UNIQUE | 아이디 (이메일 형식) |
| `password_hash` | TEXT | bcrypt 해시된 비밀번호 |
| `name` | TEXT | 사용자 실명 |
| `phone` | TEXT | 전화번호 |
| `created_at` | DATETIME | 계정 생성 일시 |
| `updated_at` | DATETIME | 최종 수정 일시 |
| `is_active` | INTEGER | 활성 상태 (1: 활성, 0: 탈퇴) |

### reset_tokens 테이블

| 컬럼 | 타입 | 설명 |
|------|------|------|
| `id` | INTEGER PK | 자동 증가 고유 번호 |
| `user_id` | INTEGER FK | 사용자 ID (users.id 참조) |
| `token` | TEXT | UUID 기반 재설정 토큰 |
| `expires_at` | DATETIME | 만료 일시 (발급 후 30분) |
| `is_used` | INTEGER | 사용 여부 (0: 미사용, 1: 사용됨) |
| `created_at` | DATETIME | 발급 일시 |

---

## API 엔드포인트

### 공통 응답 형식

**성공**
```json
{
  "success": true,
  "message": "처리 결과 메시지",
  "data": { }
}
```

**실패**
```json
{
  "success": false,
  "message": "오류 메시지"
}
```

### 인증이 필요한 엔드포인트

`Authorization: Bearer <access_token>` 헤더를 포함해야 합니다.

---

### 헬스체크

#### `GET /api/health`

서버 동작 상태를 확인합니다.

**Response 200**
```json
{
  "success": true,
  "message": "서버가 정상 동작 중입니다.",
  "version": "1.0.0"
}
```

---

### 인증 API (`/api/auth`)

---

#### `POST /api/auth/register` — 회원가입

**Request Body**
```json
{
  "email":    "user@example.com",
  "password": "Password1!",
  "name":     "홍길동",
  "phone":    "010-1234-5678"
}
```

| 필드 | 필수 | 규칙 |
|------|------|------|
| `email` | ✅ | 이메일 형식 (최대 254자) |
| `password` | ✅ | 8자 이상, 대·소문자·숫자·특수문자 각 1개 이상 |
| `name` | ✅ | 한글 또는 영문, 2~50자 |
| `phone` | ✅ | 010-1234-5678 형식 |

**Response 201**
```json
{
  "success": true,
  "message": "회원가입이 완료되었습니다."
}
```

**Error Cases**
| 상태코드 | 사유 |
|----------|------|
| 400 | 필수 항목 누락, 형식 오류 |
| 400 | 이미 사용 중인 이메일 |

---

#### `POST /api/auth/login` — 로그인

**Request Body**
```json
{
  "email":    "user@example.com",
  "password": "Password1!"
}
```

**Response 200**
```json
{
  "success": true,
  "message": "로그인 성공",
  "data": {
    "access_token":  "eyJhbGciOi...",
    "refresh_token": "eyJhbGciOi...",
    "token_type":    "Bearer",
    "user": {
      "id":         1,
      "email":      "user@example.com",
      "name":       "홍길동",
      "created_at": "2026-03-23 10:00:00"
    }
  }
}
```

**Error Cases**
| 상태코드 | 사유 |
|----------|------|
| 400 | 필수 항목 누락 |
| 401 | 이메일 또는 비밀번호 불일치 |
| 401 | 탈퇴한 계정 |

---

#### `POST /api/auth/logout` — 로그아웃 🔒

현재 액세스 토큰을 블랙리스트에 등록하여 무효화합니다.

**Headers**
```
Authorization: Bearer <access_token>
```

**Response 200**
```json
{
  "success": true,
  "message": "로그아웃 되었습니다."
}
```

---

#### `POST /api/auth/refresh` — 토큰 갱신 🔒

리프레시 토큰으로 새 액세스 토큰을 발급합니다.

**Headers**
```
Authorization: Bearer <refresh_token>
```

**Response 200**
```json
{
  "success": true,
  "message": "토큰이 갱신되었습니다.",
  "data": {
    "access_token": "eyJhbGciOi...",
    "token_type":   "Bearer"
  }
}
```

---

#### `POST /api/auth/find-id` — 아이디(이메일) 찾기

**Request Body**
```json
{
  "name":  "홍길동",
  "phone": "010-1234-5678"
}
```

**Response 200**
```json
{
  "success": true,
  "message": "아이디를 찾았습니다.",
  "data": {
    "email":      "us**@example.com",
    "created_at": "2026-03-23 10:00:00"
  }
}
```

---

#### `POST /api/auth/find-password` — 비밀번호 재설정 토큰 발급

**Request Body**
```json
{
  "email": "user@example.com",
  "name":  "홍길동"
}
```

**Response 200**
```json
{
  "success": true,
  "message": "비밀번호 재설정 토큰이 발급되었습니다. (유효기간 30분)",
  "data": {
    "reset_token": "550e8400-e29b-41d4-a716-446655440000",
    "expires_at":  "2026-03-23 10:30:00"
  }
}
```

---

#### `POST /api/auth/reset-password` — 비밀번호 재설정

**Request Body**
```json
{
  "reset_token":  "550e8400-e29b-41d4-a716-446655440000",
  "new_password": "NewPassword1!"
}
```

**Response 200**
```json
{
  "success": true,
  "message": "비밀번호가 성공적으로 변경되었습니다. 새 비밀번호로 로그인해주세요."
}
```

---

### 계정 관리 API (`/api/user`) 🔒

모든 엔드포인트에 `Authorization: Bearer <access_token>` 헤더가 필요합니다.

---

#### `GET /api/user/me` — 내 계정 조회

**Response 200**
```json
{
  "success": true,
  "data": {
    "id":         1,
    "email":      "user@example.com",
    "name":       "홍길동",
    "phone":      "010-1234-5678",
    "created_at": "2026-03-23 10:00:00",
    "updated_at": "2026-03-23 10:00:00"
  }
}
```

---

#### `PUT /api/user/me` — 내 계정 정보 수정

**Request Body**
```json
{
  "name":  "홍길동",
  "phone": "010-9876-5432"
}
```

**Response 200**
```json
{
  "success": true,
  "message": "계정 정보가 수정되었습니다.",
  "data": { ... }
}
```

---

#### `PUT /api/user/me/password` — 비밀번호 변경

**Request Body**
```json
{
  "current_password": "Password1!",
  "new_password":     "NewPassword1!"
}
```

**Response 200**
```json
{
  "success": true,
  "message": "비밀번호가 변경되었습니다."
}
```

---

#### `DELETE /api/user/me` — 회원 탈퇴

**Request Body**
```json
{
  "password": "Password1!"
}
```

**Response 200**
```json
{
  "success": true,
  "message": "계정이 탈퇴 처리되었습니다. 그동안 이용해주셔서 감사합니다."
}
```

---

## API 흐름 요약

```
회원가입      POST /api/auth/register
    ↓
로그인        POST /api/auth/login  →  access_token, refresh_token 발급
    ↓
인증 필요 API  Authorization: Bearer <access_token>
    ├── GET    /api/user/me              계정 조회
    ├── PUT    /api/user/me              정보 수정
    ├── PUT    /api/user/me/password     비밀번호 변경
    └── DELETE /api/user/me              회원 탈퇴
    ↓
토큰 갱신     POST /api/auth/refresh  →  새 access_token 발급
    ↓
로그아웃      POST /api/auth/logout   →  현재 토큰 무효화

비밀번호 찾기  POST /api/auth/find-password  →  reset_token 발급
    ↓
비밀번호 재설정 POST /api/auth/reset-password

아이디 찾기   POST /api/auth/find-id
```

---

## 비밀번호 규칙

| 항목 | 규칙 |
|------|------|
| 최소 길이 | 8자 이상 |
| 영문 대문자 | 1개 이상 |
| 영문 소문자 | 1개 이상 |
| 숫자 | 1개 이상 |
| 특수문자 | 1개 이상 (`!@#$%^&*` 등) |

---

## curl 테스트 예시

```bash
# 회원가입
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"Password1!","name":"홍길동","phone":"010-1234-5678"}'

# 로그인
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"Password1!"}'

# 계정 조회 (토큰 필요)
curl -X GET http://localhost:8000/api/user/me \
  -H "Authorization: Bearer <access_token>"

# 아이디 찾기
curl -X POST http://localhost:8000/api/auth/find-id \
  -H "Content-Type: application/json" \
  -d '{"name":"홍길동","phone":"010-1234-5678"}'

# 비밀번호 찾기 → 재설정
curl -X POST http://localhost:8000/api/auth/find-password \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","name":"홍길동"}'

curl -X POST http://localhost:8000/api/auth/reset-password \
  -H "Content-Type: application/json" \
  -d '{"reset_token":"<발급된 토큰>","new_password":"NewPassword1!"}'
```

---

## 주의사항

- `SECRET_KEY`, `JWT_SECRET_KEY`는 운영 환경에서 반드시 환경 변수로 교체하세요.
- JWT 블랙리스트는 메모리에 저장되므로 서버 재시작 시 초기화됩니다. 운영 환경에서는 Redis 사용을 권장합니다.
- 비밀번호 재설정 토큰은 실제 서비스에서 이메일로 발송해야 하며, 응답에 포함해서는 안 됩니다.
- 회원 탈퇴는 소프트 삭제(`is_active = 0`)로 처리되어 데이터가 보존됩니다.
- FastAPI는 `/docs` 경로에서 Swagger UI 기반의 자동 API 문서를 제공합니다.
