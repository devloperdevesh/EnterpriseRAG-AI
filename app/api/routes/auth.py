from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from app.db.deps import get_db
from app.models.user import User

from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
)

from app.core.dependencies import get_current_user
from app.reliability.rate_limit import limiter

router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)

# ======================
# Schemas
# ======================

class SignupRequest(BaseModel):
    email: EmailStr
    password: str
    tenant_id: str
    role: str = "user"


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


# ======================
# Signup
# ======================

@router.post(
    "/signup",
    status_code=status.HTTP_201_CREATED
)
def signup(
    payload: SignupRequest,
    db: Session = Depends(get_db)
):

    email = payload.email.lower().strip()

    existing_user = (
        db.query(User)
        .filter(User.email == email)
        .first()
    )

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already exists",
        )

    new_user = User(
        email=email,
        hashed_password=hash_password(payload.password),
        tenant_id=payload.tenant_id,
        role=payload.role,
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {
        "message": "User created successfully",
        "user_id": new_user.id,
    }


# ======================
# Login
# ======================

@router.post(
    "/login",
    response_model=TokenResponse
)
def login(
    payload: LoginRequest,
    db: Session = Depends(get_db)
):

    email = payload.email.lower().strip()

    user = (
        db.query(User)
        .filter(User.email == email)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    if not verify_password(
        payload.password,
        user.hashed_password
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    token = create_access_token(
        {
            "user_id": user.id,
            "tenant_id": user.tenant_id,
            "role": user.role,
        }
    )

    return {
        "access_token": token,
        "token_type": "bearer",
    }


# ======================
# Protected Route
# ======================

@router.get(
    "/secure",
    dependencies=[Depends(limiter(5, 60))]
)
def secure_route(
    user=Depends(get_current_user)
):

    return {
        "message": "Authorized",
        "user": user,
    }