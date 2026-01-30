from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr

from app.core.security import (
    verify_password,
    create_access_token,
    hash_password
)
from app.db.deps import get_db
from app.models.user import User

router = APIRouter(prefix="/auth", tags=["auth"])


# =====================================
# Request Schemas
# =====================================

class SignupRequest(BaseModel):
    email: EmailStr
    password: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


# =====================================
# Signup
# =====================================

@router.post("/signup", status_code=status.HTTP_201_CREATED)
async def signup(
    data: SignupRequest,
    db: Session = Depends(get_db)
):
    email = data.email.strip().lower()

    # Check existing user
    if db.query(User).filter(User.email == email).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already exists"
        )

    user = User(
        email=email,
        hashed_password=hash_password(data.password),
        tenant_id=None,      
        role="user"
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return {
        "message": "User created successfully",
        "user_id": user.id
    }


# =====================================
# Login
# =====================================

@router.post("/login")
async def login(
    data: LoginRequest,
    db: Session = Depends(get_db)
):
    email = data.email.strip().lower()

    user = db.query(User).filter(User.email == email).first()

    # Invalid credentials
    if not user or not verify_password(
        data.password,
        user.hashed_password     
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    access_token = create_access_token(
        data={
            "user_id": user.id,
            "tenant_id": user.tenant_id,
            "role": user.role
        }
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }
