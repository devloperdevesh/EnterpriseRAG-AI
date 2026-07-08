"""Focused regression tests for JWT security helpers."""

from datetime import timedelta
import inspect

from app.core import security


PAYLOAD = {
    "user_id": 42,
    "tenant_id": "tenant-1",
    "role": "user",
}


def test_token_round_trip_uses_configured_secret(monkeypatch):
    monkeypatch.setattr(security.settings, "SECRET_KEY", "alpha-secret")
    monkeypatch.setattr(security.settings, "ALGORITHM", "HS256")

    token = security.create_access_token(PAYLOAD, expires_delta=timedelta(minutes=5))
    decoded = security.decode_access_token(token)

    assert decoded is not None
    assert decoded["user_id"] == PAYLOAD["user_id"]
    assert decoded["tenant_id"] == PAYLOAD["tenant_id"]
    assert decoded["role"] == PAYLOAD["role"]
    assert security.verify_token(token) == decoded


def test_token_verification_breaks_after_secret_rotation(monkeypatch):
    monkeypatch.setattr(security.settings, "SECRET_KEY", "alpha-secret")
    monkeypatch.setattr(security.settings, "ALGORITHM", "HS256")

    token = security.create_access_token(PAYLOAD)

    monkeypatch.setattr(security.settings, "SECRET_KEY", "beta-secret")

    assert security.decode_access_token(token) is None
    assert security.verify_token(token) is None


def test_invalid_token_fails_cleanly(monkeypatch):
    monkeypatch.setattr(security.settings, "SECRET_KEY", "alpha-secret")
    monkeypatch.setattr(security.settings, "ALGORITHM", "HS256")

    assert security.decode_access_token("not-a-token") is None
    assert security.verify_token("not-a-token") is None


def test_legacy_hardcoded_secret_removed():
    source = inspect.getsource(security)

    assert "supersecret" not in source
    assert 'SECRET_KEY = "supersecret"' not in source