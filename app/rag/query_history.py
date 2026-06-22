"""Redis-backed, session-scoped query history.

Stores a compact observability record for each RAG query so the frontend can
surface per-query latency and retrieval metadata. This is intentionally
lightweight (issue #25, maintainer guidance):

* short-lived  -- entries expire after ``HISTORY_TTL_SECONDS``
* bounded      -- at most ``MAX_HISTORY_PER_USER`` entries per user
* best-effort  -- Redis failures (errors *or* slowness) never break, nor
                  delay, the query path

History is scoped per authenticated user under ``query_history:user:{user_id}``.
"""

import asyncio
import json
import uuid
from datetime import datetime, timezone
from typing import Any

from app.core.redis_client import get_redis

# 1 hour TTL, refreshed on every write.
HISTORY_TTL_SECONDS = 3600
# Keep only the most recent N queries per user.
MAX_HISTORY_PER_USER = 20
# Hard ceiling on any single Redis round-trip; a slower call is abandoned so
# history can never stall the request it is attached to.
HISTORY_OP_TIMEOUT_SECONDS = 2.0


def _key(user_id: Any) -> str:
    return f"query_history:user:{user_id}"


async def record_query(
    user_id: Any,
    *,
    query: str,
    answer_summary: str,
    chunk_count: int,
    top_scores: list[float],
    source_documents: list[str],
    retrieval_latency_ms: float,
    llm_latency_ms: float,
    total_latency_ms: float,
) -> dict:
    """Persist one query record to Redis (newest-first) and return it.

    Best-effort: any Redis error *or* a timeout is swallowed so a history
    write never blocks the query response path.
    """
    record = {
        "id": str(uuid.uuid4()),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "query": query,
        "answer_summary": answer_summary,
        "chunk_count": chunk_count,
        "top_scores": top_scores,
        "source_documents": source_documents,
        "retrieval_latency_ms": round(retrieval_latency_ms, 2),
        "llm_latency_ms": round(llm_latency_ms, 2),
        "total_latency_ms": round(total_latency_ms, 2),
    }

    async def _write() -> None:
        redis = await get_redis()
        key = _key(user_id)
        serialised = json.dumps(record)
        pipeline = redis.pipeline()
        pipeline.lpush(key, serialised)
        pipeline.ltrim(key, 0, MAX_HISTORY_PER_USER - 1)
        pipeline.expire(key, HISTORY_TTL_SECONDS)
        await pipeline.execute()

    try:
        await asyncio.wait_for(_write(), timeout=HISTORY_OP_TIMEOUT_SECONDS)
    except Exception:  # noqa: BLE001
        pass  # best-effort; do not propagate

    return record


async def get_history(user_id: Any, *, limit: int = MAX_HISTORY_PER_USER) -> list[dict]:
    """Return up to ``limit`` most-recent query records for ``user_id``.

    Best-effort: returns an empty list on any Redis failure or timeout.

    Args:
        user_id: The authenticated user's ID.
        limit: Maximum number of records to return.

    Returns:
        A list of query record dicts, newest-first. Empty list on error.
    """
    async def _read() -> list[dict]:
        redis = await get_redis()
        raw_entries = await redis.lrange(_key(user_id), 0, limit - 1)
        return [json.loads(e) for e in raw_entries]

    try:
        return await asyncio.wait_for(_read(), timeout=HISTORY_OP_TIMEOUT_SECONDS)
    except Exception:  # noqa: BLE001
        return []


async def delete_history(user_id: Any) -> None:
    """Delete all stored query history for ``user_id``.

    Best-effort: silently ignores Redis failures or timeouts.

    Args:
        user_id: The authenticated user's ID whose history to delete.
    """
    async def _delete() -> None:
        redis = await get_redis()
        await redis.delete(_key(user_id))

    try:
        await asyncio.wait_for(_delete(), timeout=HISTORY_OP_TIMEOUT_SECONDS)
    except Exception:  # noqa: BLE001
        pass
