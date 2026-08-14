"""Tests for metadata-aware secure retrieval layer (Issue #158)."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.rag.secure_retrieval import (
    AccessLevel,
    DocumentMetadata,
    SecureRetriever,
    attach_security_metadata,
    filter_retrieval_results,
)


class TestDocumentMetadata:
    """Tests for document metadata structure."""

    def test_document_metadata_creation(self):
        """Should create document metadata with all fields."""
        metadata = DocumentMetadata(
            doc_id="doc123",
            source="documents/test.pdf",
            chunk_index=0,
            tenant_id="tenant456",
            owner_id="user123",
            access_level=AccessLevel.INTERNAL,
            required_roles=[],
            tags=["technical"],
            created_by="user123",
            created_at="2024-01-01T00:00:00Z",
        )

        assert metadata.doc_id == "doc123"
        assert metadata.tenant_id == "tenant456"
        assert metadata.access_level == AccessLevel.INTERNAL


class TestSecureRetriever:
    """Tests for secure retriever access control."""

    def test_retriever_initialization(self):
        """Should initialize retriever with user context."""
        user_context = {
            "user_id": "user123",
            "tenant_id": "tenant456",
            "roles": ["user", "analyst"],
            "permissions": ["access:all"],
        }

        retriever = SecureRetriever(None, user_context)

        assert retriever.user_id == "user123"
        assert retriever.tenant_id == "tenant456"
        assert retriever.user_roles == ["user", "analyst"]

    def test_check_tenant_access_allowed(self):
        """Should allow access within same tenant."""
        user_context = {
            "user_id": "user123",
            "tenant_id": "tenant456",
            "roles": ["user"],
            "permissions": [],
        }
        retriever = SecureRetriever(None, user_context)

        metadata = DocumentMetadata(
            doc_id="doc123",
            source="doc.pdf",
            chunk_index=0,
            tenant_id="tenant456",  # Same tenant
            owner_id="user456",
            access_level=AccessLevel.PUBLIC,
            required_roles=[],
            tags=[],
            created_by="user456",
            created_at="2024-01-01T00:00:00Z",
        )

        access_granted, reason = retriever._check_tenant_access(metadata)
        assert access_granted is True
        assert reason is None

    def test_check_tenant_access_denied(self):
        """Should deny cross-tenant access."""
        user_context = {
            "user_id": "user123",
            "tenant_id": "tenant456",
            "roles": ["user"],
            "permissions": [],
        }
        retriever = SecureRetriever(None, user_context)

        metadata = DocumentMetadata(
            doc_id="doc123",
            source="doc.pdf",
            chunk_index=0,
            tenant_id="tenant789",  # Different tenant
            owner_id="user456",
            access_level=AccessLevel.PUBLIC,
            required_roles=[],
            tags=[],
            created_by="user456",
            created_at="2024-01-01T00:00:00Z",
        )

        access_granted, reason = retriever._check_tenant_access(metadata)
        assert access_granted is False
        assert "Cross-tenant access denied" in reason


class TestAccessLevelControl:
    """Tests for access level-based control."""

    def test_public_access_allowed(self):
        """PUBLIC access should be allowed for all users."""
        user_context = {
            "user_id": "user123",
            "tenant_id": "tenant456",
            "roles": ["user"],
            "permissions": [],
        }
        retriever = SecureRetriever(None, user_context)

        metadata = DocumentMetadata(
            doc_id="doc123",
            source="doc.pdf",
            chunk_index=0,
            tenant_id="tenant456",
            owner_id="user456",
            access_level=AccessLevel.PUBLIC,
            required_roles=[],
            tags=[],
            created_by="user456",
            created_at="2024-01-01T00:00:00Z",
        )

        access_granted, reason = retriever._check_access_level(metadata)
        assert access_granted is True

    def test_internal_access_allowed(self):
        """INTERNAL access should be allowed for authenticated users."""
        user_context = {
            "user_id": "user123",
            "tenant_id": "tenant456",
            "roles": ["user"],
            "permissions": [],
        }
        retriever = SecureRetriever(None, user_context)

        metadata = DocumentMetadata(
            doc_id="doc123",
            source="doc.pdf",
            chunk_index=0,
            tenant_id="tenant456",
            owner_id="user456",
            access_level=AccessLevel.INTERNAL,
            required_roles=[],
            tags=[],
            created_by="user456",
            created_at="2024-01-01T00:00:00Z",
        )

        access_granted, reason = retriever._check_access_level(metadata)
        assert access_granted is True

    def test_restricted_access_with_required_role(self):
        """RESTRICTED access should require specific role."""
        user_context = {
            "user_id": "user123",
            "tenant_id": "tenant456",
            "roles": ["analyst"],  # Has required role
            "permissions": [],
        }
        retriever = SecureRetriever(None, user_context)

        metadata = DocumentMetadata(
            doc_id="doc123",
            source="doc.pdf",
            chunk_index=0,
            tenant_id="tenant456",
            owner_id="user456",
            access_level=AccessLevel.RESTRICTED,
            required_roles=["analyst"],
            tags=[],
            created_by="user456",
            created_at="2024-01-01T00:00:00Z",
        )

        access_granted, reason = retriever._check_access_level(metadata)
        assert access_granted is True

    def test_restricted_access_denied_without_role(self):
        """RESTRICTED access should be denied without required role."""
        user_context = {
            "user_id": "user123",
            "tenant_id": "tenant456",
            "roles": ["user"],  # Does NOT have required role
            "permissions": [],
        }
        retriever = SecureRetriever(None, user_context)

        metadata = DocumentMetadata(
            doc_id="doc123",
            source="doc.pdf",
            chunk_index=0,
            tenant_id="tenant456",
            owner_id="user456",
            access_level=AccessLevel.RESTRICTED,
            required_roles=["analyst"],
            tags=[],
            created_by="user456",
            created_at="2024-01-01T00:00:00Z",
        )

        access_granted, reason = retriever._check_access_level(metadata)
        assert access_granted is False
        assert "Required roles not met" in reason

    def test_private_access_by_owner(self):
        """PRIVATE access should be allowed for owner."""
        user_context = {
            "user_id": "user123",  # Is the owner
            "tenant_id": "tenant456",
            "roles": ["user"],
            "permissions": [],
        }
        retriever = SecureRetriever(None, user_context)

        metadata = DocumentMetadata(
            doc_id="doc123",
            source="doc.pdf",
            chunk_index=0,
            tenant_id="tenant456",
            owner_id="user123",  # Same as user_id
            access_level=AccessLevel.PRIVATE,
            required_roles=[],
            tags=[],
            created_by="user123",
            created_at="2024-01-01T00:00:00Z",
        )

        access_granted, reason = retriever._check_access_level(metadata)
        assert access_granted is True

    def test_private_access_by_admin(self):
        """PRIVATE access should be allowed for admins."""
        user_context = {
            "user_id": "user123",
            "tenant_id": "tenant456",
            "roles": ["admin"],  # Is admin
            "permissions": [],
        }
        retriever = SecureRetriever(None, user_context)

        metadata = DocumentMetadata(
            doc_id="doc123",
            source="doc.pdf",
            chunk_index=0,
            tenant_id="tenant456",
            owner_id="user456",  # Different owner
            access_level=AccessLevel.PRIVATE,
            required_roles=[],
            tags=[],
            created_by="user456",
            created_at="2024-01-01T00:00:00Z",
        )

        access_granted, reason = retriever._check_access_level(metadata)
        assert access_granted is True

    def test_private_access_denied(self):
        """PRIVATE access should be denied for unauthorized users."""
        user_context = {
            "user_id": "user123",
            "tenant_id": "tenant456",
            "roles": ["user"],
            "permissions": [],
        }
        retriever = SecureRetriever(None, user_context)

        metadata = DocumentMetadata(
            doc_id="doc123",
            source="doc.pdf",
            chunk_index=0,
            tenant_id="tenant456",
            owner_id="user456",  # Different owner
            access_level=AccessLevel.PRIVATE,
            required_roles=[],
            tags=[],
            created_by="user456",
            created_at="2024-01-01T00:00:00Z",
        )

        access_granted, reason = retriever._check_access_level(metadata)
        assert access_granted is False


class TestSensitiveContentControl:
    """Tests for sensitive content filtering."""

    def test_sensitive_content_allowed_with_permission(self):
        """Should allow access to sensitive content with proper permission."""
        user_context = {
            "user_id": "user123",
            "tenant_id": "tenant456",
            "roles": ["user"],
            "permissions": ["access:confidential"],  # Has permission
        }
        retriever = SecureRetriever(None, user_context)

        metadata = DocumentMetadata(
            doc_id="doc123",
            source="doc.pdf",
            chunk_index=0,
            tenant_id="tenant456",
            owner_id="user456",
            access_level=AccessLevel.PUBLIC,
            required_roles=[],
            tags=["confidential"],  # Sensitive tag
            created_by="user456",
            created_at="2024-01-01T00:00:00Z",
        )

        access_granted, reason = retriever._check_content_sensitivity(metadata)
        assert access_granted is True

    def test_sensitive_content_denied_without_permission(self):
        """Should deny access to sensitive content without permission."""
        user_context = {
            "user_id": "user123",
            "tenant_id": "tenant456",
            "roles": ["user"],
            "permissions": [],  # No sensitive permissions
        }
        retriever = SecureRetriever(None, user_context)

        metadata = DocumentMetadata(
            doc_id="doc123",
            source="doc.pdf",
            chunk_index=0,
            tenant_id="tenant456",
            owner_id="user456",
            access_level=AccessLevel.PUBLIC,
            required_roles=[],
            tags=["confidential"],  # Sensitive tag
            created_by="user456",
            created_at="2024-01-01T00:00:00Z",
        )

        access_granted, reason = retriever._check_content_sensitivity(metadata)
        assert access_granted is False
        assert "Insufficient permissions" in reason


class TestAttachSecurityMetadata:
    """Tests for attaching security metadata."""

    def test_attach_metadata_to_documents(self):
        """Should attach security metadata to documents."""
        documents = [
            {"text": "Document 1", "source": "doc1.pdf"},
            {"text": "Document 2", "source": "doc2.pdf"},
        ]

        result = attach_security_metadata(
            documents=documents,
            tenant_id="tenant456",
            owner_id="user123",
            access_level=AccessLevel.INTERNAL,
            tags=["technical"],
        )

        assert len(result) == 2
        assert result[0]["metadata"]["tenant_id"] == "tenant456"
        assert result[0]["metadata"]["owner_id"] == "user123"
        assert result[0]["metadata"]["access_level"] == "internal"
        assert "technical" in result[0]["metadata"]["tags"]


@pytest.mark.asyncio
async def test_filter_retrieval_results():
    """Should filter retrieval results based on access control."""
    results = [
        {
            "text": "Public document",
            "score": 0.95,
            "metadata": {
                "doc_id": "doc1",
                "tenant_id": "tenant456",
                "access_level": "public",
                "owner_id": "user456",
                "chunk_index": 0,
                "source": "doc.pdf",
                "required_roles": [],
                "tags": [],
                "created_by": "user456",
                "created_at": "2024-01-01T00:00:00Z",
            },
        }
    ]

    user_context = {
        "user_id": "user123",
        "tenant_id": "tenant456",
        "roles": ["user"],
        "permissions": [],
    }

    filtered = await filter_retrieval_results(results, user_context)

    assert len(filtered) == 1
    assert filtered[0]["metadata"]["access_level"] == "public"
