from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from schemes.auth import SignupRequest, LoginRequest, TokenResponse
from fastapi import APIRouter
from core.security import (
    hash_password,
    verify_password,
    create_access_token,
)
from core.dependencies import get_current_user
from db.deps import get_db
from models.user import User
from fastapi import Depends
# from core.rate_limit import limiter

router = APIRouter(prefix="/auth", tags=["auth"])

# @router.get("/rag-query", dependencies=[Depends(limiter(5, 60))])
# def rag_query():
#     return {"msg": "Rate limited endpoint"}


@router.get("/secure")
def secure_route(user=Depends(get_current_user)):
    return {"message": "Authorized", "user": user}


@router.post("/signup", status_code=status.HTTP_201_CREATED)
def signup(payload: SignupRequest, db: Session = Depends(get_db)):
    email = payload.email.lower().strip()

    # Check if user already exists
    existing_user = db.query(User).filter(User.email == email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already exists",
        )

    # Create new user
    new_user = User(
        email=email,
        hashed_password=hash_password(payload.password),
        tenant_id=payload.tenant_id,   # IMPORTANT
        role="user",
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {
        "message": "User created successfully",
        "user_id": new_user.id,
    }


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    email = payload.email.lower().strip()

    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    if not verify_password(payload.password, user.hashed_password):
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
