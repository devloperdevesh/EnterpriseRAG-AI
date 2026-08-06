"""Redis-backed, tenant-scoped RAG pipeline metrics log.

Powers the observability dashboard (issue #117): unlike
:mod:`app.rag.query_history` -- which is a short-lived (1h TTL), per-user
audit trail of full query/answer text -- this module stores a compact,
tenant-wide metrics record per query (token usage, latency breakdown,
retrieval quality) for a longer window, so the dashboard can chart trends
across an entire tenant rather than a single user's session.

Design notes (shared here per CONTRIBUTING.md "share proposed API/schema
changes before major changes"):

* Storage: Redis list, mirroring the existing ``query_history`` pattern
  already used in this codebase, rather than introducing Postgres migrations
  for what is inherently rolling, expirable time-series data.
* Scope: keyed by ``tenant_id`` (falls back to ``"default"`` if absent) so
  metrics are aggregated across all users of a tenant, matching this
  project's multi-tenant model (see ``app.models.tenant``, ``User.tenant_id``).
* Retention: capped at ``MAX_METRICS_PER_TENANT`` entries with a
  ``METRICS_TTL_SECONDS`` TTL, refreshed on every write -- bounded memory,
  no manual cleanup job required.
* Best-effort: identical failure semantics to ``query_history`` -- a slow or
  unavailable Redis never blocks or fails the user-facing RAG query.
"""

import asyncio
import json
import uuid
from datetime import datetime, timezone
from typing import Any

from app.core.redis_client import get_redis
from app.rag.confidence import DEFAULT_CONFIDENCE_THRESHOLD

# Metrics are kept substantially longer than per-user query history since
# they back trend charts, not an audit trail of raw query text.
METRICS_TTL_SECONDS = 24 * 60 * 60  # 24 hours
# Keep only the most recent N metric records per tenant.
MAX_METRICS_PER_TENANT = 500
# Hard ceiling on any single Redis round-trip; a slower call is abandoned so
# metrics logging can never stall the request it is attached to.
METRICS_OP_TIMEOUT_SECONDS = 2.0

DEFAULT_TENANT_ID = "default"


def _key(tenant_id: Any) -> str:
    return f"rag_metrics:tenant:{tenant_id or DEFAULT_TENANT_ID}"


async def record_metric(
    tenant_id: Any,
    *,
    user_id: Any,
    query: str,
    prompt_tokens: int,
    completion_tokens: int,
    total_tokens: int,
    retrieval_latency_ms: float,
    llm_latency_ms: float,
    total_latency_ms: float,
    top_score: float,
    chunk_count: int,
    source_documents: list[str],
    confidence_threshold: float = DEFAULT_CONFIDENCE_THRESHOLD,
) -> dict:
    """Persist one aggregated metrics record to Redis and return it.

    Best-effort: any Redis error *or* a timeout is swallowed so a metrics
    write never blocks the query response path.
    """
    record = {
        "id": str(uuid.uuid4()),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "tenant_id": tenant_id or DEFAULT_TENANT_ID,
        "user_id": user_id,
        "query": query,
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
        "total_tokens": total_tokens,
        "retrieval_latency_ms": round(retrieval_latency_ms, 2),
        "llm_latency_ms": round(llm_latency_ms, 2),
        "total_latency_ms": round(total_latency_ms, 2),
        "top_score": round(top_score, 4),
        "chunk_count": chunk_count,
        "source_documents": source_documents,
        "is_low_confidence": top_score < confidence_threshold,
        "confidence_threshold": confidence_threshold,
    }

    async def _write() -> None:
        redis = await get_redis()
        key = _key(tenant_id)
        serialised = json.dumps(record)
        pipeline = redis.pipeline()
        pipeline.lpush(key, serialised)
        pipeline.ltrim(key, 0, MAX_METRICS_PER_TENANT - 1)
        pipeline.expire(key, METRICS_TTL_SECONDS)
        await pipeline.execute()

    try:
        await asyncio.wait_for(_write(), timeout=METRICS_OP_TIMEOUT_SECONDS)
    except Exception:  # noqa: BLE001
        pass  # best-effort; do not propagate

    return record


async def get_metrics(
    tenant_id: Any,
    *,
    limit: int = 50,
    offset: int = 0,
) -> list[dict]:
    """Return up to ``limit`` metric records for ``tenant_id``, newest-first.

    Best-effort: returns an empty list on any Redis failure or timeout.

    Args:
        tenant_id: The tenant to scope metrics to.
        limit: Maximum number of records to return (page size).
        offset: Number of most-recent records to skip (for pagination).

    Returns:
        A list of metric record dicts, newest-first. Empty list on error.
    """
    async def _read() -> list[dict]:
        redis = await get_redis()
        start = offset
        end = offset + limit - 1
        raw_entries = await redis.lrange(_key(tenant_id), start, end)
        return [json.loads(e) for e in raw_entries]

    try:
        return await asyncio.wait_for(_read(), timeout=METRICS_OP_TIMEOUT_SECONDS)
    except Exception:  # noqa: BLE001
        return []


async def count_metrics(tenant_id: Any) -> int:
    """Return the total number of stored metric records for ``tenant_id``.

    Used alongside :func:`get_metrics` to compute pagination metadata.
    Best-effort: returns 0 on any Redis failure or timeout.
    """
    async def _count() -> int:
        redis = await get_redis()
        return await redis.llen(_key(tenant_id))

    try:
        return await asyncio.wait_for(_count(), timeout=METRICS_OP_TIMEOUT_SECONDS)
    except Exception:  # noqa: BLE001
        return 0


async def get_metrics_summary(tenant_id: Any, *, sample_size: int = MAX_METRICS_PER_TENANT) -> dict:
    """Compute aggregate stats over the most recent ``sample_size`` records.

    Best-effort: returns a zeroed-out summary on any Redis failure or timeout.

    Returns:
        A dict with ``count``, ``avg_latency_ms``, ``avg_retrieval_latency_ms``,
        ``avg_llm_latency_ms``, ``total_tokens``, ``avg_tokens_per_query``, and
        ``low_confidence_count``.
    """
    entries = await get_metrics(tenant_id, limit=sample_size, offset=0)

    if not entries:
        return {
            "count": 0,
            "avg_latency_ms": 0.0,
            "avg_retrieval_latency_ms": 0.0,
            "avg_llm_latency_ms": 0.0,
            "total_tokens": 0,
            "avg_tokens_per_query": 0.0,
            "low_confidence_count": 0,
        }

    count = len(entries)
    total_tokens = sum(e["total_tokens"] for e in entries)

    return {
        "count": count,
        "avg_latency_ms": round(sum(e["total_latency_ms"] for e in entries) / count, 2),
        "avg_retrieval_latency_ms": round(
            sum(e["retrieval_latency_ms"] for e in entries) / count, 2
        ),
        "avg_llm_latency_ms": round(sum(e["llm_latency_ms"] for e in entries) / count, 2),
        "total_tokens": total_tokens,
        "avg_tokens_per_query": round(total_tokens / count, 2),
        "low_confidence_count": sum(1 for e in entries if e["is_low_confidence"]),
    }
