"""Tests for the query audit log endpoint."""

from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def mock_user():
    class _User:
        id = "user-test-001"
    return _User()


def test_get_audit_log_returns_entries(mock_user):
    """GET /api/rag/audit-log should return user's history entries."""
    sample_entries = [
        {
            "id": "abc123",
            "timestamp": "2026-06-22T06:00:00+00:00",
            "query": "What is RAG?",
            "answer_summary": "RAG stands for Retrieval-Augmented Generation.",
            "chunk_count": 3,
            "top_scores": [0.92, 0.87, 0.81],
            "source_documents": ["rag_overview.pdf"],
            "retrieval_latency_ms": 45.2,
            "llm_latency_ms": 312.5,
            "total_latency_ms": 357.7,
        }
    ]

    with patch(
        "app.api.routes.audit_log.get_history",
        new=AsyncMock(return_value=sample_entries),
    ), patch(
        "app.api.routes.audit_log.get_current_user",
        return_value=mock_user,
    ):
        from app.api.routes.audit_log import router
        from fastapi import FastAPI

        app = FastAPI()
        app.include_router(router)
        client = TestClient(app)

        response = client.get("/api/rag/audit-log")

    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == "user-test-001"
    assert data["count"] == 1
    assert data["entries"][0]["query"] == "What is RAG?"


def test_clear_audit_log(mock_user):
    """DELETE /api/rag/audit-log should clear user history."""
    with patch(
        "app.api.routes.audit_log.delete_history",
        new=AsyncMock(return_value=None),
    ), patch(
        "app.api.routes.audit_log.get_current_user",
        return_value=mock_user,
    ):
        from app.api.routes.audit_log import router
        from fastapi import FastAPI

        app = FastAPI()
        app.include_router(router)
        client = TestClient(app)

        response = client.delete("/api/rag/audit-log")

    assert response.status_code == 200
    assert "cleared" in response.json()["message"].lower()
