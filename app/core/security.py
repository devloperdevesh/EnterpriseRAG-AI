from datetime import datetime, timedelta
from typing import Optional

from jose import jwt, JWTError
from passlib.context import CryptContext

from app.core.config import settings

# ===============================
# Password hashing context
# ===============================
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)

# ===============================
# PASSWORD UTILITIES
# ===============================

def hash_password(password: str) -> str:
    # bcrypt supports max 72 bytes
    password_bytes = password.encode("utf-8")[:72]
    return pwd_context.hash(password_bytes)


def verify_password(password: str, hashed_password: str) -> bool:
    password_bytes = password.encode("utf-8")[:72]
    return pwd_context.verify(password_bytes, hashed_password)

# ===============================
# JWT UTILITIES
# ===============================

def create_access_token(
    data: dict,
    expires_delta: Optional[timedelta] = None
) -> str:
    to_encode = data.copy()

    expire = datetime.utcnow() + (
        expires_delta
        if expires_delta
        else timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    to_encode.update({
        "exp": expire,
        "sub": str(data.get("user_id"))  # STANDARD & SAFE
    })

    return jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm="HS256"
    )


def decode_access_token(token: str) -> Optional[dict]:
    try:
        return jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=["HS256"]
        )
    except JWTError:
        return None
