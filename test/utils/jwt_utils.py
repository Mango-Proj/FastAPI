"""
utils/jwt_utils.py
─────────────────────────────────────────
JWT 토큰 생성 및 검증 유틸리티 모듈.

주요 기능:
  - create_access_token()  : 액세스 토큰 생성
  - create_refresh_token() : 리프레시 토큰 생성
  - verify_token()         : 토큰 검증 및 페이로드 반환
"""

import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional

from jose import JWTError, jwt

from config import Config

# ─── 토큰 타입 상수 ──────────────────────────────
TOKEN_TYPE_ACCESS  = "access"
TOKEN_TYPE_REFRESH = "refresh"


def create_access_token(user_id: str) -> str:
    """
    액세스 토큰을 생성합니다.

    페이로드 구성:
      - sub  : 사용자 ID (subject)
      - type : 토큰 타입 ("access")
      - jti  : 고유 토큰 ID (JWT ID, 블랙리스트 처리에 사용)
      - exp  : 만료 일시

    Args:
        user_id: 토큰에 담을 사용자 ID (문자열)

    Returns:
        str: 서명된 JWT 액세스 토큰
    """
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=Config.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
    )

    payload = {
        "sub":  user_id,
        "type": TOKEN_TYPE_ACCESS,
        "jti":  str(uuid.uuid4()),  # 블랙리스트 처리를 위한 고유 ID
        "exp":  expire,
    }

    return jwt.encode(payload, Config.JWT_SECRET_KEY, algorithm=Config.JWT_ALGORITHM)


def create_refresh_token(user_id: str) -> str:
    """
    리프레시 토큰을 생성합니다.

    액세스 토큰 만료 시 새로운 액세스 토큰을 발급받는 데 사용합니다.

    Args:
        user_id: 토큰에 담을 사용자 ID (문자열)

    Returns:
        str: 서명된 JWT 리프레시 토큰
    """
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=Config.JWT_REFRESH_TOKEN_EXPIRE_MINUTES
    )

    payload = {
        "sub":  user_id,
        "type": TOKEN_TYPE_REFRESH,
        "jti":  str(uuid.uuid4()),
        "exp":  expire,
    }

    return jwt.encode(payload, Config.JWT_SECRET_KEY, algorithm=Config.JWT_ALGORITHM)


def verify_token(token: str, token_type: str = TOKEN_TYPE_ACCESS) -> Optional[dict]:
    """
    JWT 토큰을 검증하고 페이로드를 반환합니다.

    검증 항목:
      - 서명 유효성
      - 만료 여부
      - 토큰 타입 일치 여부

    Args:
        token      : 검증할 JWT 토큰 문자열
        token_type : 예상되는 토큰 타입 ("access" 또는 "refresh")

    Returns:
        dict  : 검증 성공 시 토큰 페이로드
        None  : 검증 실패 시 (만료, 서명 불일치, 타입 불일치 등)
    """
    try:
        payload = jwt.decode(
            token,
            Config.JWT_SECRET_KEY,
            algorithms=[Config.JWT_ALGORITHM]
        )

        # 토큰 타입 확인
        if payload.get("type") != token_type:
            return None

        return payload

    except JWTError:
        # 서명 불일치, 만료 등 모든 JWT 오류
        return None
