"""
utils/validators.py
─────────────────────────────────────────
API 요청 입력값의 유효성을 검사하는 유틸리티 함수 모음.

각 함수는 유효하면 (True, None),
유효하지 않으면 (False, "오류 메시지") 를 반환합니다.
"""

import re
from typing import Tuple, Optional


# ─── 이메일 유효성 검사 ──────────────────────────

# 이메일 형식 정규식
# 예) user@example.com, user.name+tag@sub.domain.co.kr
EMAIL_PATTERN = re.compile(
    r"^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$"
)


def validate_email(email: str) -> Tuple[bool, Optional[str]]:
    """
    이메일 형식의 유효성을 검사합니다.

    Args:
        email: 검사할 이메일 문자열

    Returns:
        (True, None)          : 유효한 이메일
        (False, "오류 메시지") : 유효하지 않은 이메일
    """
    if not email or not isinstance(email, str):
        return False, "이메일을 입력해주세요."

    email = email.strip()

    if len(email) > 254:  # RFC 5321 최대 이메일 길이
        return False, "이메일이 너무 깁니다. (최대 254자)"

    if not EMAIL_PATTERN.match(email):
        return False, "올바른 이메일 형식이 아닙니다. (예: user@example.com)"

    return True, None


# ─── 비밀번호 유효성 검사 ────────────────────────

def validate_password(password: str) -> Tuple[bool, Optional[str]]:
    """
    비밀번호 강도 규칙을 검사합니다.

    규칙:
      - 최소 8자 이상
      - 영문 대문자 1개 이상
      - 영문 소문자 1개 이상
      - 숫자 1개 이상
      - 특수문자 1개 이상 (!@#$%^&*...)

    Args:
        password: 검사할 비밀번호 문자열

    Returns:
        (True, None)          : 유효한 비밀번호
        (False, "오류 메시지") : 유효하지 않은 비밀번호
    """
    if not password or not isinstance(password, str):
        return False, "비밀번호를 입력해주세요."

    if len(password) < 8:
        return False, "비밀번호는 최소 8자 이상이어야 합니다."

    if len(password) > 128:
        return False, "비밀번호가 너무 깁니다. (최대 128자)"

    if not re.search(r"[A-Z]", password):
        return False, "비밀번호에 영문 대문자가 최소 1개 포함되어야 합니다."

    if not re.search(r"[a-z]", password):
        return False, "비밀번호에 영문 소문자가 최소 1개 포함되어야 합니다."

    if not re.search(r"\d", password):
        return False, "비밀번호에 숫자가 최소 1개 포함되어야 합니다."

    if not re.search(r"[!@#$%^&*(),.?\":{}|<>\-_=+\[\]\\;'/`~]", password):
        return False, "비밀번호에 특수문자가 최소 1개 포함되어야 합니다."

    return True, None


# ─── 이름 유효성 검사 ────────────────────────────

def validate_name(name: str) -> Tuple[bool, Optional[str]]:
    """
    사용자 이름의 유효성을 검사합니다.

    규칙:
      - 2자 이상 50자 이하
      - 한글, 영문, 공백만 허용

    Args:
        name: 검사할 이름 문자열

    Returns:
        (True, None)          : 유효한 이름
        (False, "오류 메시지") : 유효하지 않은 이름
    """
    if not name or not isinstance(name, str):
        return False, "이름을 입력해주세요."

    name = name.strip()

    if len(name) < 2:
        return False, "이름은 최소 2자 이상이어야 합니다."

    if len(name) > 50:
        return False, "이름이 너무 깁니다. (최대 50자)"

    # 한글, 영문 대소문자, 공백만 허용
    if not re.match(r"^[가-힣a-zA-Z\s]+$", name):
        return False, "이름은 한글 또는 영문만 사용 가능합니다."

    return True, None


# ─── 전화번호 유효성 검사 ────────────────────────

# 허용 형식: 010-1234-5678, 01012345678, 02-123-4567 등
PHONE_PATTERN = re.compile(r"^0\d{1,2}[-]?\d{3,4}[-]?\d{4}$")


def validate_phone(phone: str) -> Tuple[bool, Optional[str]]:
    """
    전화번호 형식의 유효성을 검사합니다.

    허용 형식:
      - 010-1234-5678
      - 01012345678
      - 02-1234-5678

    Args:
        phone: 검사할 전화번호 문자열

    Returns:
        (True, None)          : 유효한 전화번호
        (False, "오류 메시지") : 유효하지 않은 전화번호
    """
    if not phone or not isinstance(phone, str):
        return False, "전화번호를 입력해주세요."

    # 하이픈(-) 제거 후 숫자만 검사
    phone_clean = phone.replace("-", "").replace(" ", "")

    if not phone_clean.isdigit():
        return False, "전화번호는 숫자와 하이픈(-)만 입력 가능합니다."

    if not PHONE_PATTERN.match(phone):
        return False, "올바른 전화번호 형식이 아닙니다. (예: 010-1234-5678)"

    return True, None


# ─── 공통: 필수 필드 존재 여부 검사 ──────────────

def require_fields(data: dict, fields: list) -> Tuple[bool, Optional[str]]:
    """
    요청 데이터에 필수 필드가 모두 존재하는지 검사합니다.

    Args:
        data  : 요청 JSON 데이터 딕셔너리
        fields: 필수 필드명 리스트

    Returns:
        (True, None)          : 모든 필드 존재
        (False, "오류 메시지") : 누락된 필드 있음
    """
    missing = [f for f in fields if not data.get(f)]
    if missing:
        return False, f"필수 항목이 누락되었습니다: {', '.join(missing)}"
    return True, None
