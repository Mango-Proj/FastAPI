"""
routes/auth.py
─────────────────────────────────────────
인증(Authentication) 관련 API 엔드포인트 모음.

등록된 라우트:
  POST /api/auth/register        회원가입
  POST /api/auth/login           로그인
  POST /api/auth/logout          로그아웃 (JWT 필요)
  POST /api/auth/refresh         액세스 토큰 갱신 (리프레시 토큰 필요)
  POST /api/auth/find-id         아이디(이메일) 찾기
  POST /api/auth/find-password   비밀번호 재설정 토큰 발급
  POST /api/auth/reset-password  비밀번호 재설정
"""

import uuid
from datetime import datetime, timedelta

from fastapi import APIRouter, Header, HTTPException
from fastapi.responses import JSONResponse
from passlib.context import CryptContext

from config import Config
from database import get_db
from store import jwt_blocklist
from utils.jwt_utils import (
    TOKEN_TYPE_ACCESS,
    TOKEN_TYPE_REFRESH,
    create_access_token,
    create_refresh_token,
    verify_token,
)
from utils.validators import (
    require_fields,
    validate_email,
    validate_name,
    validate_password,
    validate_phone,
)

# APIRouter 생성 - URL prefix는 main.py에서 '/api/auth'로 등록됩니다
router = APIRouter()

# ─── 비밀번호 해시 컨텍스트 ──────────────────────
# bcrypt 알고리즘으로 비밀번호를 안전하게 해시합니다
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# ─── 의존성: JWT 액세스 토큰 검증 ────────────────
async def get_current_user_id(authorization: str = Header(...)) -> str:
    """
    Authorization 헤더에서 액세스 토큰을 추출하고 검증합니다.
    FastAPI의 Depends()와 함께 사용하는 의존성 함수입니다.

    Args:
        authorization: "Bearer <token>" 형식의 Authorization 헤더

    Returns:
        str: 검증된 사용자 ID

    Raises:
        HTTPException 401: 토큰 없음, 형식 오류, 만료, 블랙리스트 등
    """
    # "Bearer <token>" 형식 파싱
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="인증 토큰이 필요합니다.")

    token = authorization.split(" ", 1)[1]

    payload = verify_token(token, TOKEN_TYPE_ACCESS)
    if payload is None:
        raise HTTPException(status_code=401, detail="유효하지 않거나 만료된 토큰입니다.")

    # 블랙리스트(로그아웃된 토큰) 확인
    jti = payload.get("jti")
    if jti in jwt_blocklist:
        raise HTTPException(status_code=401, detail="로그아웃된 토큰입니다. 다시 로그인해주세요.")

    return payload["sub"]


# ─── 의존성: JWT 리프레시 토큰 검증 ──────────────
async def get_refresh_user_id(authorization: str = Header(...)) -> dict:
    """
    Authorization 헤더에서 리프레시 토큰을 추출하고 검증합니다.

    Returns:
        dict: {"user_id": str, "jti": str}

    Raises:
        HTTPException 401: 토큰 없음, 형식 오류, 만료 등
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="인증 토큰이 필요합니다.")

    token = authorization.split(" ", 1)[1]

    payload = verify_token(token, TOKEN_TYPE_REFRESH)
    if payload is None:
        raise HTTPException(status_code=401, detail="유효하지 않거나 만료된 리프레시 토큰입니다.")

    return {"user_id": payload["sub"], "jti": payload.get("jti")}


# ════════════════════════════════════════════
#  POST /api/auth/register  |  회원가입
# ════════════════════════════════════════════
@router.post("/register", status_code=201)
async def register(body: dict):
    """
    새로운 사용자 계정을 생성합니다.

    Request Body (JSON):
        email    (str, required): 이메일 형식의 아이디
        password (str, required): 비밀번호 (대·소문자·숫자·특수문자 포함 8자 이상)
        name     (str, required): 사용자 실명
        phone    (str, required): 전화번호 (예: 010-1234-5678)

    Response:
        201: 회원가입 성공
        400: 입력값 오류 또는 이미 존재하는 이메일
        500: 서버 오류
    """
    # ── 1. 필수 필드 존재 여부 확인 ─────────────
    ok, msg = require_fields(body, ["email", "password", "name", "phone"])
    if not ok:
        return JSONResponse(status_code=400, content={"success": False, "message": msg})

    email    = body["email"].strip().lower()   # 이메일은 소문자로 정규화
    password = body["password"]
    name     = body["name"].strip()
    phone    = body["phone"].strip()

    # ── 2. 각 필드 유효성 검사 ───────────────────
    ok, msg = validate_email(email)
    if not ok:
        return JSONResponse(status_code=400, content={"success": False, "message": msg})

    ok, msg = validate_password(password)
    if not ok:
        return JSONResponse(status_code=400, content={"success": False, "message": msg})

    ok, msg = validate_name(name)
    if not ok:
        return JSONResponse(status_code=400, content={"success": False, "message": msg})

    ok, msg = validate_phone(phone)
    if not ok:
        return JSONResponse(status_code=400, content={"success": False, "message": msg})

    # ── 3. 이메일 중복 확인 및 사용자 저장 ───────
    conn = get_db()
    try:
        existing = conn.execute(
            "SELECT id FROM users WHERE email = ?", (email,)
        ).fetchone()

        if existing:
            return JSONResponse(status_code=400, content={"success": False, "message": "이미 사용 중인 이메일입니다."})

        # ── 4. 비밀번호 해시화 후 사용자 저장 ────
        # passlib의 bcrypt로 안전하게 해시합니다
        password_hash = pwd_context.hash(password)

        conn.execute(
            """
            INSERT INTO users (email, password_hash, name, phone)
            VALUES (?, ?, ?, ?)
            """,
            (email, password_hash, name, phone),
        )
        conn.commit()

        return JSONResponse(status_code=201, content={
            "success": True,
            "message": "회원가입이 완료되었습니다.",
        })

    except Exception as e:
        conn.rollback()
        return JSONResponse(status_code=500, content={"success": False, "message": f"서버 오류: {str(e)}"})
    finally:
        conn.close()


# ════════════════════════════════════════════
#  POST /api/auth/login  |  로그인
# ════════════════════════════════════════════
@router.post("/login")
async def login(body: dict):
    """
    이메일과 비밀번호로 로그인하여 JWT 토큰을 발급합니다.

    Request Body (JSON):
        email    (str, required): 이메일 아이디
        password (str, required): 비밀번호

    Response:
        200: 로그인 성공 → access_token, refresh_token, user 정보 반환
        400: 필수 항목 누락
        401: 이메일 또는 비밀번호 불일치 / 탈퇴한 계정
        500: 서버 오류
    """
    # ── 1. 필수 필드 확인 ────────────────────────
    ok, msg = require_fields(body, ["email", "password"])
    if not ok:
        return JSONResponse(status_code=400, content={"success": False, "message": msg})

    email    = body["email"].strip().lower()
    password = body["password"]

    conn = get_db()
    try:
        # ── 2. 사용자 조회 ───────────────────────
        user = conn.execute(
            "SELECT * FROM users WHERE email = ?", (email,)
        ).fetchone()

        # 존재하지 않는 이메일 (보안상 이유로 공통 메시지 반환)
        if not user:
            return JSONResponse(status_code=401, content={"success": False, "message": "이메일 또는 비밀번호가 올바르지 않습니다."})

        # ── 3. 탈퇴 계정 확인 ───────────────────
        if not user["is_active"]:
            return JSONResponse(status_code=401, content={"success": False, "message": "탈퇴한 계정입니다."})

        # ── 4. 비밀번호 검증 ─────────────────────
        # passlib의 verify로 해시와 평문 비밀번호를 안전하게 비교합니다
        if not pwd_context.verify(password, user["password_hash"]):
            return JSONResponse(status_code=401, content={"success": False, "message": "이메일 또는 비밀번호가 올바르지 않습니다."})

        # ── 5. JWT 토큰 발급 ─────────────────────
        # identity: 토큰에 담을 사용자 식별 정보 (user_id를 문자열로 저장)
        identity = str(user["id"])

        # 액세스 토큰: API 요청 인증에 사용 (유효기간 1시간)
        access_token = create_access_token(identity)

        # 리프레시 토큰: 액세스 토큰 만료 시 재발급에 사용 (유효기간 30일)
        refresh_token = create_refresh_token(identity)

        return JSONResponse(status_code=200, content={
            "success": True,
            "message": "로그인 성공",
            "data": {
                "access_token":  access_token,
                "refresh_token": refresh_token,
                "token_type":    "Bearer",
                "user": {
                    "id":         user["id"],
                    "email":      user["email"],
                    "name":       user["name"],
                    "created_at": user["created_at"],
                },
            },
        })

    except Exception as e:
        return JSONResponse(status_code=500, content={"success": False, "message": f"서버 오류: {str(e)}"})
    finally:
        conn.close()


# ════════════════════════════════════════════
#  POST /api/auth/logout  |  로그아웃
# ════════════════════════════════════════════
@router.post("/logout")
async def logout(authorization: str = Header(...)):
    """
    현재 액세스 토큰을 블랙리스트에 등록하여 무효화합니다.

    Headers:
        Authorization: Bearer <access_token>

    Response:
        200: 로그아웃 성공
        401: 토큰 없음 / 만료 / 블랙리스트 등록된 토큰
    """
    if not authorization or not authorization.startswith("Bearer "):
        return JSONResponse(status_code=401, content={"success": False, "message": "인증 토큰이 필요합니다."})

    token = authorization.split(" ", 1)[1]

    payload = verify_token(token, TOKEN_TYPE_ACCESS)
    if payload is None:
        return JSONResponse(status_code=401, content={"success": False, "message": "유효하지 않거나 만료된 토큰입니다."})

    # JTI(JWT ID)를 블랙리스트에 추가 → 이 토큰은 이후 요청에서 사용 불가
    jti = payload.get("jti")
    jwt_blocklist.add(jti)

    return JSONResponse(status_code=200, content={"success": True, "message": "로그아웃 되었습니다."})


# ════════════════════════════════════════════
#  POST /api/auth/refresh  |  액세스 토큰 갱신
# ════════════════════════════════════════════
@router.post("/refresh")
async def refresh(authorization: str = Header(...)):
    """
    만료된 액세스 토큰을 리프레시 토큰으로 갱신합니다.

    Headers:
        Authorization: Bearer <refresh_token>

    Response:
        200: 새로운 access_token 반환
        401: 리프레시 토큰 없음 / 만료
    """
    if not authorization or not authorization.startswith("Bearer "):
        return JSONResponse(status_code=401, content={"success": False, "message": "인증 토큰이 필요합니다."})

    token = authorization.split(" ", 1)[1]

    # 리프레시 토큰 전용 검증
    payload = verify_token(token, TOKEN_TYPE_REFRESH)
    if payload is None:
        return JSONResponse(status_code=401, content={"success": False, "message": "유효하지 않거나 만료된 리프레시 토큰입니다."})

    # 리프레시 토큰에서 사용자 ID 추출 후 새 액세스 토큰 발급
    identity = payload["sub"]
    new_access_token = create_access_token(identity)

    return JSONResponse(status_code=200, content={
        "success": True,
        "message": "토큰이 갱신되었습니다.",
        "data": {
            "access_token": new_access_token,
            "token_type":   "Bearer",
        },
    })


# ════════════════════════════════════════════
#  POST /api/auth/find-id  |  아이디(이메일) 찾기
# ════════════════════════════════════════════
@router.post("/find-id")
async def find_id(body: dict):
    """
    이름과 전화번호로 등록된 아이디(이메일)를 찾습니다.

    Request Body (JSON):
        name  (str, required): 가입 시 등록한 실명
        phone (str, required): 가입 시 등록한 전화번호

    Response:
        200: 이메일 반환 (일부 마스킹 처리)
        400: 필수 항목 누락
        404: 일치하는 계정 없음
        500: 서버 오류
    """
    # ── 1. 필수 필드 확인 ────────────────────────
    ok, msg = require_fields(body, ["name", "phone"])
    if not ok:
        return JSONResponse(status_code=400, content={"success": False, "message": msg})

    name  = body["name"].strip()
    phone = body["phone"].strip()

    conn = get_db()
    try:
        # ── 2. 이름 + 전화번호로 사용자 조회 ────
        user = conn.execute(
            "SELECT email, created_at FROM users WHERE name = ? AND phone = ? AND is_active = 1",
            (name, phone),
        ).fetchone()

        if not user:
            return JSONResponse(status_code=404, content={"success": False, "message": "입력한 정보와 일치하는 계정이 없습니다."})

        # ── 3. 이메일 마스킹 처리 ────────────────
        # 보안상 이메일 전체를 노출하지 않고 일부만 보여줍니다.
        # 예) user@example.com  →  us**@example.com
        email = user["email"]
        local, domain = email.split("@")
        masked_local = local[:2] + "*" * max(len(local) - 2, 1)
        masked_email = f"{masked_local}@{domain}"

        return JSONResponse(status_code=200, content={
            "success": True,
            "message": "아이디를 찾았습니다.",
            "data": {
                "email":      masked_email,
                "created_at": user["created_at"],
            },
        })

    except Exception as e:
        return JSONResponse(status_code=500, content={"success": False, "message": f"서버 오류: {str(e)}"})
    finally:
        conn.close()


# ════════════════════════════════════════════
#  POST /api/auth/find-password  |  비밀번호 재설정 토큰 발급
# ════════════════════════════════════════════
@router.post("/find-password")
async def find_password(body: dict):
    """
    이메일과 이름으로 본인 확인 후 비밀번호 재설정 토큰을 발급합니다.

    실제 서비스에서는 이 토큰을 이메일로 발송합니다.
    이 API에서는 테스트 편의를 위해 응답에 토큰을 직접 반환합니다.

    Request Body (JSON):
        email (str, required): 가입한 이메일 아이디
        name  (str, required): 가입 시 등록한 실명

    Response:
        200: 재설정 토큰 반환 (유효기간 30분)
        400: 필수 항목 누락
        404: 일치하는 계정 없음
        500: 서버 오류
    """
    # ── 1. 필수 필드 확인 ────────────────────────
    ok, msg = require_fields(body, ["email", "name"])
    if not ok:
        return JSONResponse(status_code=400, content={"success": False, "message": msg})

    email = body["email"].strip().lower()
    name  = body["name"].strip()

    conn = get_db()
    try:
        # ── 2. 이메일 + 이름으로 사용자 확인 ────
        user = conn.execute(
            "SELECT id FROM users WHERE email = ? AND name = ? AND is_active = 1",
            (email, name),
        ).fetchone()

        if not user:
            return JSONResponse(status_code=404, content={"success": False, "message": "입력한 정보와 일치하는 계정이 없습니다."})

        # ── 3. 기존 미사용 토큰 무효화 ──────────
        # 동일 사용자의 이전 재설정 토큰이 남아있으면 모두 만료 처리합니다
        conn.execute(
            "UPDATE reset_tokens SET is_used = 1 WHERE user_id = ? AND is_used = 0",
            (user["id"],),
        )

        # ── 4. 새 재설정 토큰 생성 및 저장 ─────
        # UUID4 기반의 안전한 랜덤 토큰 생성
        reset_token = str(uuid.uuid4())

        # 토큰 만료 시간 계산 (현재 시간 + 30분)
        expires_at = datetime.utcnow() + timedelta(
            minutes=Config.RESET_TOKEN_EXPIRES_MINUTES
        )

        conn.execute(
            """
            INSERT INTO reset_tokens (user_id, token, expires_at)
            VALUES (?, ?, ?)
            """,
            (user["id"], reset_token, expires_at.strftime("%Y-%m-%d %H:%M:%S")),
        )
        conn.commit()

        return JSONResponse(status_code=200, content={
            "success": True,
            "message": "비밀번호 재설정 토큰이 발급되었습니다. (유효기간 30분)",
            "data": {
                # ※ 실제 서비스에서는 이 토큰을 이메일로 발송하고 응답에 포함시키지 않습니다
                "reset_token": reset_token,
                "expires_at":  expires_at.strftime("%Y-%m-%d %H:%M:%S"),
            },
        })

    except Exception as e:
        conn.rollback()
        return JSONResponse(status_code=500, content={"success": False, "message": f"서버 오류: {str(e)}"})
    finally:
        conn.close()


# ════════════════════════════════════════════
#  POST /api/auth/reset-password  |  비밀번호 재설정
# ════════════════════════════════════════════
@router.post("/reset-password")
async def reset_password(body: dict):
    """
    발급된 재설정 토큰과 새 비밀번호로 비밀번호를 변경합니다.

    Request Body (JSON):
        reset_token  (str, required): find-password에서 발급받은 토큰
        new_password (str, required): 새로운 비밀번호

    Response:
        200: 비밀번호 변경 성공
        400: 필수 항목 누락 / 비밀번호 형식 오류 / 만료된 토큰 / 이미 사용된 토큰
        404: 유효하지 않은 토큰
        500: 서버 오류
    """
    # ── 1. 필수 필드 확인 ────────────────────────
    ok, msg = require_fields(body, ["reset_token", "new_password"])
    if not ok:
        return JSONResponse(status_code=400, content={"success": False, "message": msg})

    reset_token  = body["reset_token"].strip()
    new_password = body["new_password"]

    # ── 2. 새 비밀번호 유효성 검사 ──────────────
    ok, msg = validate_password(new_password)
    if not ok:
        return JSONResponse(status_code=400, content={"success": False, "message": msg})

    conn = get_db()
    try:
        # ── 3. 토큰 조회 및 검증 ─────────────────
        token_row = conn.execute(
            "SELECT * FROM reset_tokens WHERE token = ?", (reset_token,)
        ).fetchone()

        # 존재하지 않는 토큰
        if not token_row:
            return JSONResponse(status_code=404, content={"success": False, "message": "유효하지 않은 재설정 토큰입니다."})

        # 이미 사용된 토큰
        if token_row["is_used"]:
            return JSONResponse(status_code=400, content={"success": False, "message": "이미 사용된 재설정 토큰입니다."})

        # 만료된 토큰 확인
        expires_at = datetime.strptime(token_row["expires_at"], "%Y-%m-%d %H:%M:%S")
        if datetime.utcnow() > expires_at:
            return JSONResponse(status_code=400, content={"success": False, "message": "재설정 토큰이 만료되었습니다. 다시 요청해주세요."})

        # ── 4. 비밀번호 해시화 및 업데이트 ─────
        new_password_hash = pwd_context.hash(new_password)

        conn.execute(
            """
            UPDATE users
            SET password_hash = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (new_password_hash, token_row["user_id"]),
        )

        # ── 5. 사용된 토큰 처리 ──────────────────
        conn.execute(
            "UPDATE reset_tokens SET is_used = 1 WHERE id = ?",
            (token_row["id"],),
        )

        conn.commit()

        return JSONResponse(status_code=200, content={
            "success": True,
            "message": "비밀번호가 성공적으로 변경되었습니다. 새 비밀번호로 로그인해주세요.",
        })

    except Exception as e:
        conn.rollback()
        return JSONResponse(status_code=500, content={"success": False, "message": f"서버 오류: {str(e)}"})
    finally:
        conn.close()
