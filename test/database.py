"""
database.py
─────────────────────────────────────────
SQLite 데이터베이스 연결 및 초기화를 담당하는 모듈.

주요 기능:
  - get_db()  : 데이터베이스 연결 객체 반환
  - init_db() : 테이블 생성 (애플리케이션 최초 실행 시 호출)
"""

import sqlite3
from config import Config


def get_db() -> sqlite3.Connection:
    """
    SQLite 데이터베이스 연결을 생성하여 반환합니다.

    row_factory를 sqlite3.Row로 설정하면 쿼리 결과를
    딕셔너리처럼 컬럼명으로 접근할 수 있습니다.
    예) row["email"] 또는 dict(row)

    Returns:
        sqlite3.Connection: 데이터베이스 연결 객체
    """
    conn = sqlite3.connect(Config.DATABASE_PATH)
    conn.row_factory = sqlite3.Row  # 결과를 딕셔너리 형태로 반환
    conn.execute("PRAGMA foreign_keys = ON")  # 외래 키 제약 조건 활성화
    return conn


def init_db() -> None:
    """
    데이터베이스 테이블을 초기화합니다.
    이미 테이블이 존재하면 건너뜁니다 (IF NOT EXISTS).

    생성 테이블:
      1. users        : 사용자 계정 정보
      2. reset_tokens : 비밀번호 재설정 토큰
    """
    conn = get_db()
    cursor = conn.cursor()

    # ─── 1. users 테이블 ─────────────────────────
    # 사용자 계정의 모든 정보를 저장합니다.
    # email은 로그인 아이디로 사용되며, UNIQUE 제약으로 중복을 방지합니다.
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id            INTEGER  PRIMARY KEY AUTOINCREMENT,  -- 사용자 고유 번호 (자동 증가)
            email         TEXT     UNIQUE NOT NULL,            -- 아이디 (이메일 형식, 중복 불가)
            password_hash TEXT     NOT NULL,                   -- bcrypt 해시된 비밀번호
            name          TEXT     NOT NULL,                   -- 사용자 실명
            phone         TEXT     NOT NULL,                   -- 전화번호 (아이디 찾기에 사용)
            created_at    DATETIME DEFAULT CURRENT_TIMESTAMP,  -- 계정 생성 일시
            updated_at    DATETIME DEFAULT CURRENT_TIMESTAMP,  -- 계정 정보 최종 수정 일시
            is_active     INTEGER  DEFAULT 1                   -- 활성 상태 (1: 활성, 0: 탈퇴)
        )
    """)

    # ─── 2. reset_tokens 테이블 ──────────────────
    # 비밀번호 재설정 요청 시 발급되는 임시 토큰을 저장합니다.
    # 토큰은 30분 내에 1회만 사용 가능합니다.
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS reset_tokens (
            id         INTEGER  PRIMARY KEY AUTOINCREMENT,  -- 토큰 고유 번호
            user_id    INTEGER  NOT NULL,                   -- 어느 사용자의 토큰인지
            token      TEXT     NOT NULL,                   -- UUID 기반 랜덤 토큰 문자열
            expires_at DATETIME NOT NULL,                   -- 만료 일시 (발급 후 30분)
            is_used    INTEGER  DEFAULT 0,                  -- 사용 여부 (0: 미사용, 1: 사용됨)
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,  -- 토큰 발급 일시
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """)

    conn.commit()
    conn.close()
    print("✅ 데이터베이스 초기화 완료")
