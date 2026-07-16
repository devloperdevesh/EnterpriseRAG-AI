from datetime import datetime, timedelta, timezone
from typing import Any

import jwt
from jwt import PyJWTError as JWTError
import bcrypt

from app.core.config import settings

def _normalize_password(password: str) -> bytes:
    """Limit bcrypt input to its supported 72-byte maximum."""
    return password.encode("utf-8")[:72]

def hash_password(password: str) -> str:
    pwd_bytes = _normalize_password(password)
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(pwd_bytes, salt).decode("utf-8")

def verify_password(password: str, hashed_password: str) -> bool:
    pwd_bytes = _normalize_password(password)
    hash_bytes = hashed_password.encode("utf-8")
    try:
        return bcrypt.checkpw(pwd_bytes, hash_bytes)
    except ValueError:
        return False


def create_access_token(
    data: dict[str, Any],
    expires_delta: timedelta | None = None,
) -> str:
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    subject = data.get("sub") or data.get("user_id")
    if subject is None:
        raise ValueError("JWT access tokens require a subject")

    to_encode = {
        **data,
        "exp": expire,
        "sub": str(subject),
    }
    return jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )


def decode_access_token(token: str) -> dict[str, Any] | None:
    try:
        return jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )
    except JWTError:
        return None
