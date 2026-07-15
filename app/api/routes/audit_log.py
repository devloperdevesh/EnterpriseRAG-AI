"""Query Audit Log API endpoint.

Exposes the Redis-backed per-user query history stored by
``app.rag.query_history`` through a REST endpoint. Enables compliance
audit trails and usage analytics without exposing sensitive query content
beyond the authenticated user.

Route: GET /api/rag/audit-log
"""

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.core.dependencies import get_current_user
from app.rag.query_history import (
    MAX_HISTORY_PER_USER,
    delete_history,
    get_history,
)

router = APIRouter(prefix="/api/rag", tags=["audit"])


@router.get(
    "/audit-log",
    summary="Retrieve query audit log for the authenticated user",
    description=(
        "Returns a paginated list of past RAG queries made by the current user. "
        "Entries include the original query text, answer summary, retrieval "
        "latency, and relevance scores of the top retrieved chunks. "
        "Results are returned newest-first and expire after 1 hour of inactivity."
    ),
    status_code=status.HTTP_200_OK,
)
async def get_audit_log(
    limit: int = Query(
        default=20,
        ge=1,
        le=MAX_HISTORY_PER_USER,
        description="Maximum number of entries to return (1 – 20).",
    ),
    current_user: Any = Depends(get_current_user),
) -> dict:
    """Retrieve the authenticated user’s query audit log.

    Args:
        limit: Number of most-recent entries to return.
        current_user: Injected by the auth dependency.

    Returns:
        A JSON object with ``user_id``, ``count``, and ``entries`` list.

    Raises:
        HTTPException 500: When the Redis read fails unexpectedly.
    """
    user_id = getattr(current_user, "id", None) or getattr(current_user, "user_id", None)
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not identify authenticated user.",
        )

    entries = await get_history(user_id, limit=limit)

    return {
        "user_id": user_id,
        "count": len(entries),
        "entries": entries,
    }


@router.delete(
    "/audit-log",
    summary="Clear query audit log for the authenticated user",
    description="Permanently deletes all stored query history for the current user.",
    status_code=status.HTTP_200_OK,
)
async def clear_audit_log(
    current_user: Any = Depends(get_current_user),
) -> dict:
    """Delete the authenticated user’s full query history from Redis.

    Args:
        current_user: Injected by the auth dependency.

    Returns:
        A confirmation message.
    """
    user_id = getattr(current_user, "id", None) or getattr(current_user, "user_id", None)
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not identify authenticated user.",
        )

    await delete_history(user_id)
    return {"message": "Query audit log cleared successfully.", "user_id": user_id}
