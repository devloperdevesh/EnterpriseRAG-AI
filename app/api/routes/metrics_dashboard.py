"""RAG Pipeline Observability Dashboard API (issue #117).

Exposes tenant-wide token usage, latency, and retrieval-quality metrics
collected by ``app.observability.metrics_log`` through a REST endpoint,
backing the ``/dashboard/observability`` frontend page.

Route: GET /api/metrics
"""

from typing import Any

from fastapi import APIRouter, Depends, Query, status

from app.core.dependencies import get_current_user
from app.observability.metrics_log import (
    MAX_METRICS_PER_TENANT,
    count_metrics,
    get_metrics,
    get_metrics_summary,
)

router = APIRouter(prefix="/api/metrics", tags=["metrics"])


@router.get(
    "",
    summary="Retrieve paginated RAG pipeline metrics for the current tenant",
    description=(
        "Returns paginated, newest-first metric records (token usage, "
        "retrieval/LLM/total latency, top retrieval score, chunk sources) "
        "for the authenticated user's tenant, plus an aggregate summary "
        "(averages, total tokens, low-confidence count) computed over the "
        "stored window. Backs the observability dashboard's charts and "
        "low-confidence alert indicator."
    ),
    status_code=status.HTTP_200_OK,
)
async def get_dashboard_metrics(
    limit: int = Query(
        default=50,
        ge=1,
        le=MAX_METRICS_PER_TENANT,
        description="Maximum number of entries to return per page.",
    ),
    offset: int = Query(
        default=0,
        ge=0,
        description="Number of most-recent entries to skip (for pagination).",
    ),
    current_user: Any = Depends(get_current_user),
) -> dict:
    """Retrieve the authenticated user's tenant-wide pipeline metrics.

    Args:
        limit: Page size.
        offset: Pagination offset from the most recent entry.
        current_user: Injected by the auth dependency.

    Returns:
        A JSON object with ``tenant_id``, ``count``, ``total``, ``limit``,
        ``offset``, ``summary``, and ``entries``.
    """
    tenant_id = current_user.get("tenant_id")

    entries = await get_metrics(tenant_id, limit=limit, offset=offset)
    total = await count_metrics(tenant_id)
    summary = await get_metrics_summary(tenant_id)

    return {
        "tenant_id": tenant_id or "default",
        "count": len(entries),
        "total": total,
        "limit": limit,
        "offset": offset,
        "summary": summary,
        "entries": entries,
    }
