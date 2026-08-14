"""Metadata-aware secure retrieval layer with access control filtering.

Issue #158: Implements document-level access control in the retrieval pipeline
to prevent unauthorized access to sensitive documents based on tenant, role, and
permission scope.

Enforces security constraints before context generation to provide stronger
security guarantees and reduce unnecessary processing of unauthorized content.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Any, Optional

from app.core.security import get_user_permissions


class AccessLevel(str, Enum):
    """Document access level within a tenant."""

    PUBLIC = "public"  # Accessible to all users in tenant
    INTERNAL = "internal"  # Accessible to authenticated users in tenant
    RESTRICTED = "restricted"  # Requires specific role
    PRIVATE = "private"  # Only document owner and admins


@dataclass
class DocumentMetadata:
    """Security and lineage metadata for document chunks."""

    doc_id: str
    source: str
    chunk_index: int
    tenant_id: str
    owner_id: str
    access_level: AccessLevel
    required_roles: list[str]  # Roles required for access
    tags: list[str]  # Document classification tags
    created_by: str
    created_at: str


@dataclass
class SecureRetrievalResult:
    """Result from secure retrieval including document and access verification."""

    chunk_text: str
    doc_id: str
    source: str
    chunk_index: int
    similarity_score: float
    metadata: DocumentMetadata
    access_granted: bool
    denial_reason: Optional[str]


class SecureRetriever:
    """Retriever with built-in access control enforcement."""

    def __init__(self, vector_store: Any, user_context: dict):
        """Initialize secure retriever.

        Args:
            vector_store: FAISS or similar vector store instance
            user_context: User information (id, tenant_id, roles)
        """
        self.vector_store = vector_store
        self.user_context = user_context
        self.user_id = user_context.get("user_id")
        self.tenant_id = user_context.get("tenant_id")
        self.user_roles = user_context.get("roles", [])
        self.permissions = user_context.get("permissions", [])

    async def retrieve_with_access_control(
        self,
        query_embedding: list[float],
        top_k: int = 10,
        min_score: float = 0.5,
    ) -> list[SecureRetrievalResult]:
        """Retrieve documents with access control filtering.

        Args:
            query_embedding: Query embedding vector
            top_k: Number of candidates to retrieve before filtering
            min_score: Minimum similarity threshold

        Returns:
            List of SecureRetrievalResult with access control decisions.
        """
        # Retrieve candidates from vector store
        candidates = self._retrieve_candidates(query_embedding, top_k)

        results = []
        for candidate in candidates:
            result = await self._check_access_and_build_result(
                candidate,
                min_score,
            )
            results.append(result)

        # Return only authorized documents
        return [r for r in results if r.access_granted]

    def _retrieve_candidates(
        self,
        query_embedding: list[float],
        top_k: int,
    ) -> list[dict]:
        """Retrieve candidate documents from vector store.

        Args:
            query_embedding: Query embedding
            top_k: Number of candidates

        Returns:
            List of candidate documents with metadata
        """
        # This would call the actual vector store
        # For now, return empty list (implementation depends on vector store)
        if hasattr(self.vector_store, "similarity_search"):
            return self.vector_store.similarity_search(query_embedding, k=top_k)
        return []

    async def _check_access_and_build_result(
        self,
        candidate: dict,
        min_score: float,
    ) -> SecureRetrievalResult:
        """Check access permissions and build result.

        Args:
            candidate: Candidate document with metadata
            min_score: Minimum similarity threshold

        Returns:
            SecureRetrievalResult with access decision
        """
        similarity_score = candidate.get("score", 0.0)
        metadata = candidate.get("metadata", {})

        # Build metadata object
        doc_metadata = DocumentMetadata(
            doc_id=metadata.get("doc_id", "unknown"),
            source=metadata.get("source", "unknown"),
            chunk_index=metadata.get("chunk_index", 0),
            tenant_id=metadata.get("tenant_id", ""),
            owner_id=metadata.get("owner_id", ""),
            access_level=AccessLevel(metadata.get("access_level", "private")),
            required_roles=metadata.get("required_roles", []),
            tags=metadata.get("tags", []),
            created_by=metadata.get("created_by", ""),
            created_at=metadata.get("created_at", ""),
        )

        # Check tenant isolation
        tenant_check, tenant_reason = self._check_tenant_access(doc_metadata)
        if not tenant_check:
            return SecureRetrievalResult(
                chunk_text="",
                doc_id=doc_metadata.doc_id,
                source=doc_metadata.source,
                chunk_index=doc_metadata.chunk_index,
                similarity_score=similarity_score,
                metadata=doc_metadata,
                access_granted=False,
                denial_reason=tenant_reason,
            )

        # Check access level and roles
        access_check, access_reason = self._check_access_level(doc_metadata)
        if not access_check:
            return SecureRetrievalResult(
                chunk_text="",
                doc_id=doc_metadata.doc_id,
                source=doc_metadata.source,
                chunk_index=doc_metadata.chunk_index,
                similarity_score=similarity_score,
                metadata=doc_metadata,
                access_granted=False,
                denial_reason=access_reason,
            )

        # Check content sensitivity
        sensitivity_check, sensitivity_reason = self._check_content_sensitivity(doc_metadata)
        if not sensitivity_check:
            return SecureRetrievalResult(
                chunk_text="",
                doc_id=doc_metadata.doc_id,
                source=doc_metadata.source,
                chunk_index=doc_metadata.chunk_index,
                similarity_score=similarity_score,
                metadata=doc_metadata,
                access_granted=False,
                denial_reason=sensitivity_reason,
            )

        # All checks passed
        return SecureRetrievalResult(
            chunk_text=candidate.get("text", ""),
            doc_id=doc_metadata.doc_id,
            source=doc_metadata.source,
            chunk_index=doc_metadata.chunk_index,
            similarity_score=similarity_score,
            metadata=doc_metadata,
            access_granted=True,
            denial_reason=None,
        )

    def _check_tenant_access(self, metadata: DocumentMetadata) -> tuple[bool, Optional[str]]:
        """Verify tenant isolation.

        Args:
            metadata: Document metadata

        Returns:
            Tuple of (access_granted, denial_reason)
        """
        # Enforce strict tenant isolation
        if metadata.tenant_id != self.tenant_id:
            return False, f"Cross-tenant access denied: {metadata.tenant_id} != {self.tenant_id}"

        return True, None

    def _check_access_level(self, metadata: DocumentMetadata) -> tuple[bool, Optional[str]]:
        """Check document access level and required roles.

        Args:
            metadata: Document metadata

        Returns:
            Tuple of (access_granted, denial_reason)
        """
        access_level = metadata.access_level

        # PUBLIC: accessible to all authenticated users
        if access_level == AccessLevel.PUBLIC:
            return True, None

        # INTERNAL: accessible to any authenticated user in tenant
        if access_level == AccessLevel.INTERNAL:
            return True, None

        # RESTRICTED: requires specific role
        if access_level == AccessLevel.RESTRICTED:
            if not metadata.required_roles:
                return True, None

            # Check if user has any required role
            user_has_role = any(role in self.user_roles for role in metadata.required_roles)
            if not user_has_role:
                return False, f"Required roles not met: {metadata.required_roles}"

            return True, None

        # PRIVATE: only owner and admins
        if access_level == AccessLevel.PRIVATE:
            is_owner = self.user_id == metadata.owner_id
            is_admin = "admin" in self.user_roles

            if not (is_owner or is_admin):
                return False, "Private document: only owner and admins can access"

            return True, None

        return False, f"Unknown access level: {access_level}"

    def _check_content_sensitivity(
        self,
        metadata: DocumentMetadata,
    ) -> tuple[bool, Optional[str]]:
        """Check content sensitivity and user permissions.

        Args:
            metadata: Document metadata

        Returns:
            Tuple of (access_granted, denial_reason)
        """
        # Check for sensitive tags
        sensitive_tags = {"confidential", "pii", "health", "financial"}
        doc_tags = set(metadata.tags)

        restricted_tags = sensitive_tags & doc_tags

        if restricted_tags:
            # User needs specific permission for sensitive content
            required_permissions = {f"access:{tag}" for tag in restricted_tags}
            user_permissions = set(self.permissions)

            if not required_permissions.issubset(user_permissions):
                missing = required_permissions - user_permissions
                return False, f"Insufficient permissions for sensitive content: {missing}"

        return True, None


async def filter_retrieval_results(
    results: list[dict],
    user_context: dict,
) -> list[dict]:
    """Filter retrieval results based on access control.

    Standalone function for filtering retrieval results after vector search.

    Args:
        results: Raw retrieval results from vector store
        user_context: User information (id, tenant_id, roles)

    Returns:
        Filtered results containing only authorized documents
    """
    retriever = SecureRetriever(None, user_context)

    filtered = []
    for result in results:
        check_result = await retriever._check_access_and_build_result(
            result,
            min_score=0.0,
        )

        if check_result.access_granted:
            filtered.append(result)

    return filtered


def attach_security_metadata(
    documents: list[dict],
    tenant_id: str,
    owner_id: str,
    access_level: AccessLevel = AccessLevel.INTERNAL,
    required_roles: Optional[list[str]] = None,
    tags: Optional[list[str]] = None,
) -> list[dict]:
    """Attach security metadata to documents for indexing.

    Args:
        documents: List of documents to attach metadata to
        tenant_id: Tenant identifier
        owner_id: Document owner identifier
        access_level: Access level for the document
        required_roles: Roles required for access (if RESTRICTED)
        tags: Document classification tags

    Returns:
        Documents with security metadata attached
    """
    for doc in documents:
        doc["metadata"] = {
            "tenant_id": tenant_id,
            "owner_id": owner_id,
            "access_level": access_level.value,
            "required_roles": required_roles or [],
            "tags": tags or [],
            "created_by": owner_id,
            "created_at": doc.get("created_at", ""),
        }

    return documents
