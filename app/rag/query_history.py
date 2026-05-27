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
    outage can never fail -- or slow down -- an otherwise-successful RAG query.
    Callers typically dispatch this fire-and-forget.
    """
    record = {
        "id": uuid.uuid4().hex,
        "query": query,
        "answer_summary": answer_summary,
        "chunk_count": chunk_count,
        "top_scores": top_scores,
        "source_documents": source_documents,
        "retrieval_latency_ms": retrieval_latency_ms,
        "llm_latency_ms": llm_latency_ms,
        "total_latency_ms": total_latency_ms,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

    key = _key(user_id)
    try:
        redis = get_redis()
        # Single round-trip: prepend, trim to cap, refresh TTL.
        pipe = redis.pipeline()
        pipe.lpush(key, json.dumps(record))
        pipe.ltrim(key, 0, MAX_HISTORY_PER_USER - 1)
        pipe.expire(key, HISTORY_TTL_SECONDS)
        await asyncio.wait_for(pipe.execute(), timeout=HISTORY_OP_TIMEOUT_SECONDS)
    except Exception:  # pragma: no cover - history is observability-only
        # Intentionally silent: never let history break the query path.
        pass

    return record


async def get_history(user_id: Any, limit: int = MAX_HISTORY_PER_USER) -> list[dict]:
    """Return up to ``limit`` most-recent query records for ``user_id``.

    Returns an empty list if Redis is unavailable, too slow, or the user has
    no history.
    """
    limit = max(1, min(limit, MAX_HISTORY_PER_USER))
    try:
        redis = get_redis()
        raw_entries = await asyncio.wait_for(
            redis.lrange(_key(user_id), 0, limit - 1),
            timeout=HISTORY_OP_TIMEOUT_SECONDS,
        )
    except Exception:  # pragma: no cover - history is observability-only
        return []

    history: list[dict] = []
    for raw in raw_entries:
        try:
            history.append(json.loads(raw))
        except (json.JSONDecodeError, TypeError):
            # Skip corrupt entries rather than failing the whole response.
            continue
    return history
