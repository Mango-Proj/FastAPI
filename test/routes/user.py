"""
routes/user.py
─────────────────────────────────────────
로그인된 사용자의 계정 관리 API 엔드포인트 모음.
모든 엔드포인트는 유효한 JWT 액세스 토큰이 필요합니다.

등록된 라우트:
  GET    /api/user/me           내 계정 정보 조회
  PUT    /api/user/me           내 계정 정보 수정 (이름, 전화번호)
  PUT    /api/user/me/password  비밀번호 변경
  DELETE /api/user/me           회원 탈퇴
"""

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from passlib.context import CryptContext

from database import get_db
from routes.auth import get_current_user_id
from utils.validators import validate_name, validate_password, validate_phone

# Blueprint 생성 - URL prefix는 main.py에서 '/api/user'로 등록됩니다
router = APIRouter()

# ─── 비밀번호 해시 컨텍스트 ──────────────────────
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# ════════════════════════════════════════════
#  GET /api/user/me  |  내 계정 정보 조회
# ════════════════════════════════════════════
@router.get("/me")
async def get_me(user_id: str = Depends(get_current_user_id)):
    """
    현재 로그인한 사용자의 계정 정보를 반환합니다.
    비밀번호 해시는 응답에 포함되지 않습니다.

    Headers:
        Authorization: Bearer <access_token>

    Response:
        200: 사용자 정보 반환
        401: 토큰 없음 / 만료
        404: 계정 없음 (탈퇴한 계정)
        500: 서버 오류
    """
    conn = get_db()
    try:
        # ── 사용자 정보 조회 (비밀번호 해시 제외) ─
        user = conn.execute(
            """
            SELECT id, email, name, phone, created_at, updated_at
            FROM users
            WHERE id = ? AND is_active = 1
            """,
            (int(user_id),),
        ).fetchone()

        if not user:
            return JSONResponse(status_code=404, content={"success": False, "message": "계정 정보를 찾을 수 없습니다."})

        return JSONResponse(status_code=200, content={
            "success": True,
            "data": {
                "id":         user["id"],
                "email":      user["email"],
                "name":       user["name"],
                "phone":      user["phone"],
                "created_at": user["created_at"],
                "updated_at": user["updated_at"],
            },
        })

    except Exception as e:
        return JSONResponse(status_code=500, content={"success": False, "message": f"서버 오류: {str(e)}"})
    finally:
        conn.close()


# ════════════════════════════════════════════
#  PUT /api/user/me  |  내 계정 정보 수정
# ════════════════════════════════════════════
@router.put("/me")
async def update_me(body: dict, user_id: str = Depends(get_current_user_id)):
    """
    현재 로그인한 사용자의 이름 또는 전화번호를 수정합니다.
    변경할 항목만 요청에 포함하면 됩니다 (부분 업데이트 지원).

    Headers:
        Authorization: Bearer <access_token>

    Request Body (JSON, 하나 이상 필수):
        name  (str, optional): 변경할 이름
        phone (str, optional): 변경할 전화번호

    Response:
        200: 수정 성공 → 업데이트된 사용자 정보 반환
        400: 수정할 항목 없음 / 유효성 오류
        401: 토큰 없음 / 만료
        404: 계정 없음
        500: 서버 오류
    """
    # ── 1. 수정할 항목 수집 ──────────────────────
    # 요청에 포함된 항목만 업데이트합니다
    updates = {}

    if "name" in body and body["name"]:
        ok, msg = validate_name(body["name"].strip())
        if not ok:
            return JSONResponse(status_code=400, content={"success": False, "message": msg})
        updates["name"] = body["name"].strip()

    if "phone" in body and body["phone"]:
        ok, msg = validate_phone(body["phone"].strip())
        if not ok:
            return JSONResponse(status_code=400, content={"success": False, "message": msg})
        updates["phone"] = body["phone"].strip()

    # 수정할 항목이 하나도 없을 때
    if not updates:
        return JSONResponse(status_code=400, content={"success": False, "message": "수정할 항목(name, phone)을 입력해주세요."})

    conn = get_db()
    try:
        # ── 2. 계정 존재 여부 확인 ───────────────
        user = conn.execute(
            "SELECT id FROM users WHERE id = ? AND is_active = 1", (int(user_id),)
        ).fetchone()

        if not user:
            return JSONResponse(status_code=404, content={"success": False, "message": "계정 정보를 찾을 수 없습니다."})

        # ── 3. 동적 UPDATE 쿼리 생성 ─────────────
        # 변경 항목에 따라 SET 절을 동적으로 조합합니다
        set_clauses = [f"{col} = ?" for col in updates.keys()]
        set_clauses.append("updated_at = CURRENT_TIMESTAMP")
        values = list(updates.values()) + [int(user_id)]

        conn.execute(
            f"UPDATE users SET {', '.join(set_clauses)} WHERE id = ?",
            values,
        )
        conn.commit()

        # ── 4. 업데이트된 사용자 정보 반환 ──────
        updated_user = conn.execute(
            "SELECT id, email, name, phone, created_at, updated_at FROM users WHERE id = ?",
            (int(user_id),),
        ).fetchone()

        return JSONResponse(status_code=200, content={
            "success": True,
            "message": "계정 정보가 수정되었습니다.",
            "data": {
                "id":         updated_user["id"],
                "email":      updated_user["email"],
                "name":       updated_user["name"],
                "phone":      updated_user["phone"],
                "created_at": updated_user["created_at"],
                "updated_at": updated_user["updated_at"],
            },
        })

    except Exception as e:
        conn.rollback()
        return JSONResponse(status_code=500, content={"success": False, "message": f"서버 오류: {str(e)}"})
    finally:
        conn.close()


# ════════════════════════════════════════════
#  PUT /api/user/me/password  |  비밀번호 변경
# ════════════════════════════════════════════
@router.put("/me/password")
async def change_password(body: dict, user_id: str = Depends(get_current_user_id)):
    """
    현재 비밀번호를 확인한 후 새 비밀번호로 변경합니다.
    (로그인된 상태에서의 비밀번호 변경 기능입니다.)

    Headers:
        Authorization: Bearer <access_token>

    Request Body (JSON):
        current_password (str, required): 현재 비밀번호
        new_password     (str, required): 새로운 비밀번호

    Response:
        200: 비밀번호 변경 성공
        400: 필수 항목 누락 / 새 비밀번호 형식 오류 / 현재 비밀번호 불일치
        401: 토큰 없음 / 만료
        404: 계정 없음
        500: 서버 오류
    """
    # ── 1. 필수 필드 확인 ────────────────────────
    current_password = body.get("current_password", "")
    new_password     = body.get("new_password", "")

    if not current_password:
        return JSONResponse(status_code=400, content={"success": False, "message": "현재 비밀번호를 입력해주세요."})
    if not new_password:
        return JSONResponse(status_code=400, content={"success": False, "message": "새 비밀번호를 입력해주세요."})

    # ── 2. 새 비밀번호 유효성 검사 ──────────────
    ok, msg = validate_password(new_password)
    if not ok:
        return JSONResponse(status_code=400, content={"success": False, "message": msg})

    conn = get_db()
    try:
        # ── 3. 현재 사용자 조회 ──────────────────
        user = conn.execute(
            "SELECT * FROM users WHERE id = ? AND is_active = 1", (int(user_id),)
        ).fetchone()

        if not user:
            return JSONResponse(status_code=404, content={"success": False, "message": "계정 정보를 찾을 수 없습니다."})

        # ── 4. 현재 비밀번호 검증 ────────────────
        if not pwd_context.verify(current_password, user["password_hash"]):
            return JSONResponse(status_code=400, content={"success": False, "message": "현재 비밀번호가 올바르지 않습니다."})

        # ── 5. 현재 비밀번호와 새 비밀번호 동일 여부 확인 ─
        if pwd_context.verify(new_password, user["password_hash"]):
            return JSONResponse(status_code=400, content={"success": False, "message": "새 비밀번호는 현재 비밀번호와 달라야 합니다."})

        # ── 6. 새 비밀번호로 업데이트 ───────────
        new_password_hash = pwd_context.hash(new_password)

        conn.execute(
            """
            UPDATE users
            SET password_hash = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (new_password_hash, int(user_id)),
        )
        conn.commit()

        return JSONResponse(status_code=200, content={
            "success": True,
            "message": "비밀번호가 변경되었습니다.",
        })

    except Exception as e:
        conn.rollback()
        return JSONResponse(status_code=500, content={"success": False, "message": f"서버 오류: {str(e)}"})
    finally:
        conn.close()


# ════════════════════════════════════════════
#  DELETE /api/user/me  |  회원 탈퇴
# ════════════════════════════════════════════
@router.delete("/me")
async def delete_me(body: dict, user_id: str = Depends(get_current_user_id)):
    """
    계정을 탈퇴 처리합니다. (소프트 삭제: is_active = 0)
    실제 데이터는 보존되며 is_active 플래그만 0으로 변경됩니다.

    Headers:
        Authorization: Bearer <access_token>

    Request Body (JSON):
        password (str, required): 탈퇴 확인용 현재 비밀번호

    Response:
        200: 탈퇴 성공
        400: 비밀번호 누락 / 비밀번호 불일치
        401: 토큰 없음 / 만료
        404: 계정 없음
        500: 서버 오류
    """
    # ── 1. 탈퇴 확인용 비밀번호 확인 ────────────
    password = body.get("password", "")
    if not password:
        return JSONResponse(status_code=400, content={"success": False, "message": "탈퇴 확인을 위해 비밀번호를 입력해주세요."})

    conn = get_db()
    try:
        # ── 2. 사용자 조회 ───────────────────────
        user = conn.execute(
            "SELECT * FROM users WHERE id = ? AND is_active = 1", (int(user_id),)
        ).fetchone()

        if not user:
            return JSONResponse(status_code=404, content={"success": False, "message": "계정 정보를 찾을 수 없습니다."})

        # ── 3. 비밀번호 검증 ─────────────────────
        if not pwd_context.verify(password, user["password_hash"]):
            return JSONResponse(status_code=400, content={"success": False, "message": "비밀번호가 올바르지 않습니다."})

        # ── 4. 소프트 삭제 (is_active = 0 으로 변경) ─
        # 완전 삭제(DELETE) 대신 비활성화하여 데이터 보존 및 복구 가능성을 남깁니다
        conn.execute(
            """
            UPDATE users
            SET is_active = 0, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (int(user_id),),
        )
        conn.commit()

        return JSONResponse(status_code=200, content={
            "success": True,
            "message": "계정이 탈퇴 처리되었습니다. 그동안 이용해주셔서 감사합니다.",
        })

    except Exception as e:
        conn.rollback()
        return JSONResponse(status_code=500, content={"success": False, "message": f"서버 오류: {str(e)}"})
    finally:
        conn.close()
