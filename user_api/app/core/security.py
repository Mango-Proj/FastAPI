from passlib.context import CryptContext

# CryptContext 설정: bcrypt 방식을 사용하며, 폐기된 방식은 자동으로 처리합니다.
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str):
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)
