import os
from datetime import datetime, timedelta, timezone
from typing import Optional, Tuple
from jose import jwt, JWTError
from passlib.context import CryptContext
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", "change-me")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
REFRESH_TOKEN_EXPIRE_MINUTES = int(os.getenv("REFRESH_TOKEN_EXPIRE_MINUTES", "43200"))  # 30 days default
ADMIN_TOKEN = os.getenv("ADMIN_TOKEN", "admin-change-me")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def _create_token(data: dict, minutes: int) -> str:
    to_encode = data.copy()
    now = datetime.now(timezone.utc)
    expire = now + timedelta(minutes=minutes)
    # Use current timestamp as a simple unique identifier
    to_encode.update({
        "iat": now,  # Issued at time
        "exp": expire,
        "jti": str(int(now.timestamp() * 1000))  # Use timestamp as unique ID
    })
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    payload = data.copy()
    payload.setdefault("type", "access")
    if expires_delta is not None:
        minutes = int(expires_delta.total_seconds() // 60)
    else:
        minutes = ACCESS_TOKEN_EXPIRE_MINUTES
    return _create_token(payload, minutes)


def create_refresh_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    payload = data.copy()
    payload.setdefault("type", "refresh")
    if expires_delta is not None:
        minutes = int(expires_delta.total_seconds() // 60)
    else:
        minutes = REFRESH_TOKEN_EXPIRE_MINUTES
    return _create_token(payload, minutes)


def decode_token(token: str) -> Optional[dict]:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None


def get_current_user(token: str, expected_type: Optional[str] = None) -> Optional[Tuple[str, int]]:
    """
    Returns (role, user_id) if token valid, else None.
    Token is expected to carry claims: {"role": "patient"|"doctor", "user_id": int, "type": "access"|"refresh"}
    If expected_type is provided, token must match that type.
    """
    payload = decode_token(token)
    if not payload:
        return None
    role = payload.get("role")
    user_id = payload.get("user_id")
    token_type = payload.get("type")
    if expected_type and token_type != expected_type:
        return None
    if role not in ("patient", "doctor", "admin") or not isinstance(user_id, int):
        return None
    return role, user_id
