"""
Tests for POST /documents/preview-chunks (Issue #1 API endpoint)
Uses FastAPI TestClient with auth mocked out.
"""

import io
import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from fastapi import FastAPI

from app.core.dependencies import get_current_user
from app.api.routes.document import router


# ---------------------------------------------------------------------------
# Minimal app fixture with auth bypassed via dependency_overrides
# ---------------------------------------------------------------------------

FAKE_USER = {"user_id": "u1", "tenant_id": "t1", "role": "user"}


@pytest.fixture
def client():
    app = FastAPI()
    app.include_router(router)
    app.dependency_overrides[get_current_user] = lambda: FAKE_USER
    with TestClient(app) as c:
        yield c


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestPreviewChunksEndpoint:
    def test_rejects_non_pdf(self, client):
        data = io.BytesIO(b"not a pdf")
        resp = client.post(
            "/documents/preview-chunks",
            files={"file": ("test.txt", data, "text/plain")},
        )
        assert resp.status_code == 400
        assert "PDF" in resp.json()["detail"]

    def test_valid_pdf_returns_200(self, client):
        """Mock PyPDF2 to return known text so we don't need a real PDF."""
        with patch("app.api.routes.document.PyPDF2.PdfReader") as mock_reader:
            mock_page = MagicMock()
            mock_page.extract_text.return_value = " ".join([f"word{i}" for i in range(600)])
            mock_reader.return_value.pages = [mock_page]

            pdf_bytes = io.BytesIO(b"%PDF-1.4 fake")
            resp = client.post(
                "/documents/preview-chunks?chunk_size=200&overlap=20",
                files={"file": ("doc.pdf", pdf_bytes, "application/pdf")},
            )
        assert resp.status_code == 200

    def test_response_structure(self, client):
        with patch("app.api.routes.document.PyPDF2.PdfReader") as mock_reader:
            mock_page = MagicMock()
            mock_page.extract_text.return_value = " ".join([f"word{i}" for i in range(600)])
            mock_reader.return_value.pages = [mock_page]

            pdf_bytes = io.BytesIO(b"%PDF-1.4 fake")
            resp = client.post(
                "/documents/preview-chunks?chunk_size=200&overlap=20",
                files={"file": ("doc.pdf", pdf_bytes, "application/pdf")},
            )

        body = resp.json()
        assert "total_words" in body
        assert "total_chunks" in body
        assert "chunk_size" in body
        assert "overlap" in body
        assert "chunks" in body
        assert isinstance(body["chunks"], list)

    def test_chunk_fields_present(self, client):
        with patch("app.api.routes.document.PyPDF2.PdfReader") as mock_reader:
            mock_page = MagicMock()
            mock_page.extract_text.return_value = " ".join([f"word{i}" for i in range(300)])
            mock_reader.return_value.pages = [mock_page]

            pdf_bytes = io.BytesIO(b"%PDF-1.4 fake")
            resp = client.post(
                "/documents/preview-chunks?chunk_size=100&overlap=10",
                files={"file": ("doc.pdf", pdf_bytes, "application/pdf")},
            )

        chunk = resp.json()["chunks"][0]
        for field in ("index", "preview", "full_text", "word_count", "char_count",
                      "start_word", "end_word"):
            assert field in chunk, f"Missing field: {field}"

    def test_chunk_size_param_respected(self, client):
        with patch("app.api.routes.document.PyPDF2.PdfReader") as mock_reader:
            mock_page = MagicMock()
            mock_page.extract_text.return_value = " ".join([f"word{i}" for i in range(1000)])
            mock_reader.return_value.pages = [mock_page]

            pdf_bytes = io.BytesIO(b"%PDF-1.4 fake")
            resp_small = client.post(
                "/documents/preview-chunks?chunk_size=100&overlap=0",
                files={"file": ("doc.pdf", pdf_bytes, "application/pdf")},
            )

        with patch("app.api.routes.document.PyPDF2.PdfReader") as mock_reader:
            mock_page = MagicMock()
            mock_page.extract_text.return_value = " ".join([f"word{i}" for i in range(1000)])
            mock_reader.return_value.pages = [mock_page]

            pdf_bytes = io.BytesIO(b"%PDF-1.4 fake")
            resp_large = client.post(
                "/documents/preview-chunks?chunk_size=500&overlap=0",
                files={"file": ("doc.pdf", pdf_bytes, "application/pdf")},
            )

        assert resp_small.json()["total_chunks"] > resp_large.json()["total_chunks"]

    def test_empty_pdf_returns_422(self, client):
        with patch("app.api.routes.document.PyPDF2.PdfReader") as mock_reader:
            mock_page = MagicMock()
            mock_page.extract_text.return_value = ""
            mock_reader.return_value.pages = [mock_page]

            pdf_bytes = io.BytesIO(b"%PDF-1.4 fake")
            resp = client.post(
                "/documents/preview-chunks",
                files={"file": ("empty.pdf", pdf_bytes, "application/pdf")},
            )
        assert resp.status_code == 422
