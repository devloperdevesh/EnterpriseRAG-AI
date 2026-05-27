"""Tests for the Redis-backed query history feature (issue #25).

These run hermetically against an in-memory fake Redis -- no external Redis
server, embedding model or LLM is required.
"""

import asyncio

import numpy as np
import pytest
from fakeredis import FakeAsyncRedis

from app.rag import query_history, vector_store
from app.rag.query_history import (
    HISTORY_TTL_SECONDS,
    MAX_HISTORY_PER_USER,
    get_history,
    record_query,
)
from app.rag.vector_store import add_embedding, search_embedding_scored

USER_ID = 42


# --------------------------------------------------------------------------
# query_history (Redis storage)
# --------------------------------------------------------------------------
@pytest.fixture()
def fake_redis(monkeypatch):
    """Point query_history at a fresh in-memory Redis for each test."""
    client = FakeAsyncRedis(decode_responses=True)
    monkeypatch.setattr(query_history, "get_redis", lambda: client)
    return client


def _sample(query="What is the refund policy?"):
    """A representative record payload for record_query()."""
    return dict(
        query=query,
        answer_summary="Refunds are processed within 14 business days.",
        chunk_count=3,
        top_scores=[0.83, 0.71, 0.65],
        source_documents=["policy.pdf"],
        retrieval_latency_ms=42.7,
        llm_latency_ms=1830.4,
        total_latency_ms=1873.1,
    )


def test_record_and_read_back(fake_redis):
    async def scenario():
        record = await record_query(USER_ID, **_sample())
        return record, await get_history(USER_ID)

    record, history = asyncio.run(scenario())

    assert len(history) == 1
    entry = history[0]
    for field in (
        "id", "query", "answer_summary", "chunk_count", "top_scores",
        "source_documents", "retrieval_latency_ms", "llm_latency_ms",
        "total_latency_ms", "timestamp",
    ):
        assert field in entry, f"missing field: {field}"
    assert entry["id"] == record["id"]
    assert entry["query"] == "What is the refund policy?"
    assert entry["total_latency_ms"] == 1873.1
    assert entry["source_documents"] == ["policy.pdf"]


def test_newest_first_ordering(fake_redis):
    async def scenario():
        for label in ("first", "second", "third"):
            await record_query(USER_ID, **_sample(label))
        return await get_history(USER_ID)

    history = asyncio.run(scenario())
    assert [e["query"] for e in history] == ["third", "second", "first"]


def test_limit_param(fake_redis):
    async def scenario():
        for i in range(5):
            await record_query(USER_ID, **_sample(f"q{i}"))
        return await get_history(USER_ID, limit=2)

    history = asyncio.run(scenario())
    assert len(history) == 2
    assert history[0]["query"] == "q4"


def test_history_is_capped(fake_redis):
    async def scenario():
        for i in range(MAX_HISTORY_PER_USER + 8):
            await record_query(USER_ID, **_sample(f"q{i}"))
        stored = await fake_redis.llen(query_history._key(USER_ID))
        return stored, await get_history(USER_ID, limit=MAX_HISTORY_PER_USER)

    stored, history = asyncio.run(scenario())
    assert stored == MAX_HISTORY_PER_USER
    assert len(history) == MAX_HISTORY_PER_USER
    # Oldest entries were trimmed; the most recent survives.
    assert history[0]["query"] == f"q{MAX_HISTORY_PER_USER + 7}"


def test_ttl_is_applied(fake_redis):
    async def scenario():
        await record_query(USER_ID, **_sample())
        return await fake_redis.ttl(query_history._key(USER_ID))

    ttl = asyncio.run(scenario())
    assert 0 < ttl <= HISTORY_TTL_SECONDS


def test_history_is_user_scoped(fake_redis):
    async def scenario():
        await record_query(1, **_sample("user one query"))
        return await get_history(2)

    assert asyncio.run(scenario()) == []


# --------------------------------------------------------------------------
# vector_store.search_embedding_scored (retrieval metadata)
# --------------------------------------------------------------------------
@pytest.fixture()
def clean_vector_store():
    """Reset the in-memory FAISS index around each test."""
    def _reset():
        vector_store.index.reset()
        vector_store.documents.clear()
        vector_store.sources.clear()

    _reset()
    yield
    _reset()


def _vec(seed):
    rng = np.random.default_rng(seed)
    return rng.random(vector_store.EMBEDDING_DIM, dtype=np.float32).tolist()


def test_scored_search_returns_score_and_source(clean_vector_store):
    add_embedding(_vec(1), "chunk about refunds", source="policy.pdf")
    add_embedding(_vec(2), "chunk about leave", source="handbook.pdf")

    results = search_embedding_scored(_vec(1), top_k=2)

    assert len(results) == 2
    for chunk in results:
        assert set(chunk.keys()) == {"text", "score", "source"}
        assert 0.0 < chunk["score"] <= 1.0
    # The exact query vector is its own nearest neighbour.
    assert results[0]["text"] == "chunk about refunds"
    assert results[0]["source"] == "policy.pdf"


def test_scored_search_empty_index(clean_vector_store):
    assert search_embedding_scored(_vec(1), top_k=3) == []
