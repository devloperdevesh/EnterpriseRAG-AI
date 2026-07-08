from datetime import datetime, timedelta, timezone
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
    """Hash a plaintext password using bcrypt."""
    # bcrypt supports max 72 bytes
    password_bytes = password.encode("utf-8")[:72]
    return pwd_context.hash(password_bytes)


def verify_password(password: str, hashed_password: str) -> bool:
    """Verify a plaintext password against a bcrypt hash."""
    password_bytes = password.encode("utf-8")[:72]
    return pwd_context.verify(password_bytes, hashed_password)


# ===============================
# TOKEN UTILITIES
# ===============================

def create_access_token(
    data: dict,
    expires_delta: Optional[timedelta] = None,
) -> str:
    """
    Create a signed JWT access token.

    Uses settings.SECRET_KEY and settings.ALGORITHM from app config.
    Never hardcodes the secret — all secrets must come from environment variables.
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta
        if expires_delta is not None
        else timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def verify_token(token: str) -> Optional[dict]:
    """Decode and validate a JWT token. Returns the payload dict or None if invalid."""
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )
        return payload
    except JWTError:
        return None
