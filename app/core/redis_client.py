"""Shared async Redis client.

A single lazily-initialised ``redis.asyncio`` connection pool reused across the
app (query history, and available for future short-lived caches). Host/port are
read from the environment so deployments can override them, defaulting to the
same local Redis used by :mod:`app.reliability.rate_limit`.
"""

import os

import redis.asyncio as redis

_client: "redis.Redis | None" = None


def get_redis() -> "redis.Redis":
    """Return the process-wide async Redis client, creating it on first use.

    ``decode_responses=True`` so callers get ``str`` values back instead of
    bytes, which keeps JSON (de)serialisation straightforward.
    """
    global _client
    if _client is None:
        _client = redis.Redis(
            host=os.getenv("REDIS_HOST", "localhost"),
            port=int(os.getenv("REDIS_PORT", "6379")),
            db=int(os.getenv("REDIS_DB", "0")),
            decode_responses=True,
        )
    return _client


async def close_redis() -> None:
    """Close the client (useful for app shutdown / test teardown)."""
    global _client
    if _client is not None:
        await _client.aclose()
        _client = None
