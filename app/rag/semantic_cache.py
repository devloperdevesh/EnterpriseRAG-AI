"""Semantic query cache layer using Redis and vector similarity matching.

Issue #161: Implements caching for repeated queries using semantic similarity
to reduce embedding generation and retrieval operations.

The cache stores previous query responses with embeddings and matches similar
queries using cosine similarity. Cache entries are configurable with TTL and
size limits for enterprise workloads.
"""

import asyncio
import hashlib
import json
import time
from typing import Any, Optional

import numpy as np

from app.core.redis_client import get_redis
from app.rag.embeddings import generate_embedding

# Cache configuration constants
SEMANTIC_CACHE_TTL_SECONDS = 3600  # 1 hour TTL
SEMANTIC_CACHE_PREFIX = "semantic_cache"
SIMILARITY_THRESHOLD = 0.85  # Minimum cosine similarity for cache hit
MAX_CACHE_SIZE_PER_USER = 100  # Maximum number of cached queries per user


def _cosine_similarity(vec1: list[float], vec2: list[float]) -> float:
    """Calculate cosine similarity between two vectors."""
    arr1 = np.array(vec1)
    arr2 = np.array(vec2)

    dot_product = np.dot(arr1, arr2)
    norm1 = np.linalg.norm(arr1)
    norm2 = np.linalg.norm(arr2)

    if norm1 == 0 or norm2 == 0:
        return 0.0

    return float(dot_product / (norm1 * norm2))


def _cache_key(user_id: Any) -> str:
    """Generate cache key for a user's cached queries."""
    return f"{SEMANTIC_CACHE_PREFIX}:user:{user_id}"


def _cache_metadata_key(user_id: Any) -> str:
    """Generate metadata key for tracking cache hits/misses."""
    return f"{SEMANTIC_CACHE_PREFIX}:metadata:{user_id}"


async def get_cached_response(
    user_id: Any,
    query: str,
) -> Optional[dict]:
    """Retrieve cached response if semantically similar query exists.

    Args:
        user_id: Unique user identifier
        query: Current query string

    Returns:
        Cached response dict with 'answer', 'chunks', 'source_documents' if found,
        otherwise None.
    """
    redis_client = get_redis()

    try:
        # Generate embedding for current query
        query_embedding = generate_embedding(query)
        if not query_embedding:
            return None

        # Retrieve all cached entries for the user
        cache_key = _cache_key(user_id)
        cached_entries = await asyncio.wait_for(
            redis_client.hgetall(cache_key),
            timeout=2.0,  # Non-blocking timeout
        )

        if not cached_entries:
            return None

        # Find most similar cached query
        best_match = None
        best_similarity = 0.0

        for entry_id, entry_json in cached_entries.items():
            try:
                cached_entry = json.loads(entry_json)
                cached_embedding = cached_entry.get("embedding", [])

                if not cached_embedding:
                    continue

                similarity = _cosine_similarity(query_embedding, cached_embedding)

                if similarity > best_similarity:
                    best_similarity = similarity
                    best_match = cached_entry

            except (json.JSONDecodeError, TypeError):
                continue

        # Return cached response if similarity meets threshold
        if best_match and best_similarity >= SIMILARITY_THRESHOLD:
            # Record cache hit
            await _record_cache_hit(user_id)
            return {
                "answer": best_match.get("answer", ""),
                "chunks": best_match.get("chunks", []),
                "source_documents": best_match.get("source_documents", []),
                "similarity_score": best_similarity,
                "from_cache": True,
            }

    except asyncio.TimeoutError:
        # Non-blocking: cache lookup timed out, proceed without cache
        pass
    except Exception:
        # Fail gracefully: any cache error doesn't break the query path
        pass

    return None


async def cache_response(
    user_id: Any,
    query: str,
    answer: str,
    chunks: list[dict],
    source_documents: list[str],
) -> bool:
    """Store query response in semantic cache.

    Args:
        user_id: Unique user identifier
        query: Query string
        answer: Generated answer
        chunks: Retrieved document chunks
        source_documents: List of source document names

    Returns:
        True if successfully cached, False otherwise.
    """
    redis_client = get_redis()

    try:
        # Generate embedding for the query
        query_embedding = generate_embedding(query)
        if not query_embedding:
            return False

        # Create cache entry
        cache_entry = {
            "query": query,
            "embedding": query_embedding,
            "answer": answer,
            "chunks": chunks,
            "source_documents": source_documents,
            "cached_at": time.time(),
        }

        # Generate cache entry ID
        query_hash = hashlib.md5(query.encode()).hexdigest()
        entry_id = f"{int(time.time())}:{query_hash}"

        cache_key = _cache_key(user_id)

        # Store in Redis with timeout
        await asyncio.wait_for(
            redis_client.hset(
                cache_key,
                entry_id,
                json.dumps(cache_entry),
            ),
            timeout=2.0,
        )

        # Set TTL on the cache key
        await asyncio.wait_for(
            redis_client.expire(cache_key, SEMANTIC_CACHE_TTL_SECONDS),
            timeout=1.0,
        )

        # Enforce max cache size per user
        await _trim_cache(user_id)

        return True

    except asyncio.TimeoutError:
        # Non-blocking: cache write timed out
        return False
    except Exception:
        # Fail gracefully: cache errors don't break query path
        return False


async def _trim_cache(user_id: Any) -> None:
    """Remove oldest entries if cache exceeds max size per user.

    Keeps the most recent MAX_CACHE_SIZE_PER_USER entries.
    """
    redis_client = get_redis()

    try:
        cache_key = _cache_key(user_id)
        cache_size = await asyncio.wait_for(
            redis_client.hlen(cache_key),
            timeout=1.0,
        )

        if cache_size > MAX_CACHE_SIZE_PER_USER:
            # Get all entries and sort by timestamp
            entries = await asyncio.wait_for(
                redis_client.hgetall(cache_key),
                timeout=1.0,
            )

            entry_ids = sorted(entries.keys())
            to_delete = entry_ids[: cache_size - MAX_CACHE_SIZE_PER_USER]

            if to_delete:
                await asyncio.wait_for(
                    redis_client.hdel(cache_key, *to_delete),
                    timeout=1.0,
                )

    except (asyncio.TimeoutError, Exception):
        # Non-blocking: trimming errors don't break the query path
        pass


async def _record_cache_hit(user_id: Any) -> None:
    """Record a cache hit for metrics and monitoring."""
    redis_client = get_redis()

    try:
        metadata_key = _cache_metadata_key(user_id)

        await asyncio.wait_for(
            redis_client.hincrby(metadata_key, "cache_hits", 1),
            timeout=1.0,
        )

        # Set TTL on metadata
        await asyncio.wait_for(
            redis_client.expire(metadata_key, SEMANTIC_CACHE_TTL_SECONDS),
            timeout=1.0,
        )

    except (asyncio.TimeoutError, Exception):
        pass


async def clear_user_cache(user_id: Any) -> bool:
    """Clear all cached queries for a user.

    Useful for manual cache invalidation or user data cleanup.

    Args:
        user_id: Unique user identifier

    Returns:
        True if successfully cleared, False otherwise.
    """
    redis_client = get_redis()

    try:
        cache_key = _cache_key(user_id)
        metadata_key = _cache_metadata_key(user_id)

        await asyncio.wait_for(
            redis_client.delete(cache_key, metadata_key),
            timeout=2.0,
        )

        return True

    except Exception:
        return False


async def get_cache_stats(user_id: Any) -> dict:
    """Get cache statistics for a user.

    Returns:
        Dict with cache hit count, total cached queries, and memory usage.
    """
    redis_client = get_redis()

    try:
        cache_key = _cache_key(user_id)
        metadata_key = _cache_metadata_key(user_id)

        cache_size = await asyncio.wait_for(
            redis_client.hlen(cache_key),
            timeout=1.0,
        )

        metadata = await asyncio.wait_for(
            redis_client.hgetall(metadata_key),
            timeout=1.0,
        )

        cache_hits = int(metadata.get("cache_hits", 0))

        return {
            "cached_queries": cache_size,
            "cache_hits": cache_hits,
            "hit_rate": cache_hits / (cache_size + cache_hits) if (cache_size + cache_hits) > 0 else 0,
        }

    except Exception:
        return {
            "cached_queries": 0,
            "cache_hits": 0,
            "hit_rate": 0,
        }
