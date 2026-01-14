from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.core.security import verify_password, create_access_token, hash_password
from app.db.deps import get_db
from app.models.user import User

router = APIRouter(prefix="/auth", tags=["auth"])


# ===== Request Schemas =====

class SignupRequest(BaseModel):
    email: str
    password: str

class LoginRequest(BaseModel):
    email: str
    password: str


# ===== Signup =====
@router.post("/signup")
async def signup(data: SignupRequest, db: Session = Depends(get_db)):
    email = data.email.strip().lower()

    existing = db.query(User).filter(User.email == email).first()
    if existing:
        raise HTTPException(status_code=400, detail="User already exists")

    user = User(
        email=email,
        hashed_password=hash_password(data.password),
        tenant_id="tenant_1",
        role="user"
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return {"message": "User created successfully"}


# ===== Login =====
@router.post("/login")
async def login(data: LoginRequest, db: Session = Depends(get_db)):
    email = data.email.strip().lower()
    password = data.password

    user = db.query(User).filter(User.email == email).first()
    print("USER FROM DB:", user)

    if not user or not verify_password(password, str(user.hashed_password)):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

    token = create_access_token({
        "user_id": user.id,
        "tenant_id": user.tenant_id,
        "role": user.role
    })

    return {
        "access_token": token,
        "token_type": "bearer"
    }
