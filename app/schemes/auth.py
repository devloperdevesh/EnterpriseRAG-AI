from pydantic import BaseModel

class SignupRequest(BaseModel):
    email: str
    password: str
    tenant_id: str            # REQUIRED (DB constraint)
    role: str = "user"        # default role

class LoginRequest(BaseModel):
    email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"