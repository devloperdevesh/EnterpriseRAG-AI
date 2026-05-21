from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

from app.core.config import settings
from app.core.exceptions import AuthenticationException


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    if not token:
        raise AuthenticationException("Not authenticated")

    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )
    except JWTError as exc:
        raise AuthenticationException("Invalid token") from exc

    if payload.get("sub") is None and payload.get("user_id") is None:
        raise AuthenticationException("Invalid token")

    return {
        "user_id": payload.get("user_id"),
        "tenant_id": payload.get("tenant_id"),
        "role": payload.get("role"),
        "sub": payload.get("sub"),
    }
