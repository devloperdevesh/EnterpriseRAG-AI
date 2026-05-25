import os
from datetime import timedelta

os.environ.setdefault("DATABASE_URL", "sqlite:///./test_auth.db")
os.environ.setdefault("SECRET_KEY", "test-secret")

from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient

from app.core.dependencies import get_current_user
from app.core.security import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)


def _client():
    app = FastAPI()

    @app.get("/dashboard")
    def dashboard(user=Depends(get_current_user)):
        return {"user": user}

    return TestClient(app)


def test_access_token_contains_session_claims():
    token = create_access_token(
        {
            "user_id": 123,
            "tenant_id": "tenant-a",
            "role": "admin",
            "email": "admin@example.com",
        }
    )

    payload = decode_access_token(token)

    assert payload is not None
    assert payload["sub"] == "123"
    assert payload["tenant_id"] == "tenant-a"
    assert payload["role"] == "admin"


def test_password_hashes_verify_against_plaintext():
    hashed_password = hash_password("correct horse battery staple")

    assert verify_password("correct horse battery staple", hashed_password)
    assert not verify_password("wrong password", hashed_password)


def test_protected_route_allows_valid_bearer_token():
    token = create_access_token(
        {
            "user_id": 123,
            "tenant_id": "tenant-a",
            "role": "user",
        }
    )

    response = _client().get(
        "/dashboard",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assert response.json()["user"]["user_id"] == 123


def test_protected_route_rejects_invalid_token():
    response = _client().get(
        "/dashboard",
        headers={"Authorization": "Bearer invalid.jwt.token"},
    )

    assert response.status_code == 401


def test_protected_route_rejects_expired_token():
    token = create_access_token(
        {"user_id": 123, "tenant_id": "tenant-a"},
        expires_delta=timedelta(seconds=-1),
    )

    response = _client().get(
        "/dashboard",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 401
