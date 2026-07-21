"""Tests for the RAG observability dashboard metrics store (issue #117).

These run hermetically against an in-memory fake Redis -- no external Redis
server, embedding model or LLM is required. Mirrors the conventions used in
``test_query_history.py``.
"""

import asyncio

import pytest
from fakeredis import FakeAsyncRedis

from app.observability import metrics_log
from app.observability.metrics_log import (
    MAX_METRICS_PER_TENANT,
    METRICS_TTL_SECONDS,
    count_metrics,
    get_metrics,
    get_metrics_summary,
    record_metric,
)

TENANT_ID = "acme-corp"


@pytest.fixture()
def fake_redis(monkeypatch):
    """Point metrics_log at a fresh in-memory Redis for each test."""
    client = FakeAsyncRedis(decode_responses=True)
    monkeypatch.setattr(metrics_log, "get_redis", lambda: client)
    return client


def _sample(query="What is the refund policy?", top_score=0.83, total_tokens=180):
    """A representative record payload for record_metric()."""
    return dict(
        user_id=7,
        query=query,
        prompt_tokens=total_tokens - 40,
        completion_tokens=40,
        total_tokens=total_tokens,
        retrieval_latency_ms=42.7,
        llm_latency_ms=830.4,
        total_latency_ms=873.1,
        top_score=top_score,
        chunk_count=3,
        source_documents=["policy.pdf"],
    )


def test_record_and_read_back(fake_redis):
    async def scenario():
        record = await record_metric(TENANT_ID, **_sample())
        return record, await get_metrics(TENANT_ID)

    record, entries = asyncio.run(scenario())

    assert len(entries) == 1
    entry = entries[0]
    for field in (
        "id", "timestamp", "tenant_id", "user_id", "query", "prompt_tokens",
        "completion_tokens", "total_tokens", "retrieval_latency_ms",
        "llm_latency_ms", "total_latency_ms", "top_score", "chunk_count",
        "source_documents", "is_low_confidence", "confidence_threshold",
    ):
        assert field in entry, f"missing field: {field}"
    assert entry["id"] == record["id"]
    assert entry["tenant_id"] == TENANT_ID
    assert entry["total_tokens"] == 180


def test_low_confidence_flagging(fake_redis):
    async def scenario():
        await record_metric(TENANT_ID, **_sample("in-domain query", top_score=0.9))
        await record_metric(TENANT_ID, **_sample("out-of-domain query", top_score=0.1))
        return await get_metrics(TENANT_ID)

    entries = asyncio.run(scenario())
    by_query = {e["query"]: e for e in entries}
    assert by_query["in-domain query"]["is_low_confidence"] is False
    assert by_query["out-of-domain query"]["is_low_confidence"] is True


def test_newest_first_ordering(fake_redis):
    async def scenario():
        for label in ("first", "second", "third"):
            await record_metric(TENANT_ID, **_sample(label))
        return await get_metrics(TENANT_ID)

    entries = asyncio.run(scenario())
    assert [e["query"] for e in entries] == ["third", "second", "first"]


def test_pagination_limit_and_offset(fake_redis):
    async def scenario():
        for i in range(10):
            await record_metric(TENANT_ID, **_sample(f"q{i}"))
        page1 = await get_metrics(TENANT_ID, limit=4, offset=0)
        page2 = await get_metrics(TENANT_ID, limit=4, offset=4)
        return page1, page2

    page1, page2 = asyncio.run(scenario())
    assert [e["query"] for e in page1] == ["q9", "q8", "q7", "q6"]
    assert [e["query"] for e in page2] == ["q5", "q4", "q3", "q2"]


def test_metrics_are_capped(fake_redis):
    async def scenario():
        for i in range(MAX_METRICS_PER_TENANT + 8):
            await record_metric(TENANT_ID, **_sample(f"q{i}"))
        stored = await fake_redis.llen(metrics_log._key(TENANT_ID))
        return stored, await count_metrics(TENANT_ID)

    stored, total = asyncio.run(scenario())
    assert stored == MAX_METRICS_PER_TENANT
    assert total == MAX_METRICS_PER_TENANT


def test_ttl_is_applied(fake_redis):
    async def scenario():
        await record_metric(TENANT_ID, **_sample())
        return await fake_redis.ttl(metrics_log._key(TENANT_ID))

    ttl = asyncio.run(scenario())
    assert 0 < ttl <= METRICS_TTL_SECONDS


def test_metrics_are_tenant_scoped(fake_redis):
    async def scenario():
        await record_metric("tenant-a", **_sample("tenant a query"))
        return await get_metrics("tenant-b")

    assert asyncio.run(scenario()) == []


def test_metrics_default_tenant_fallback(fake_redis):
    async def scenario():
        await record_metric(None, **_sample())
        return await get_metrics(None)

    entries = asyncio.run(scenario())
    assert len(entries) == 1
    assert entries[0]["tenant_id"] == "default"


def test_summary_aggregates_correctly(fake_redis):
    async def scenario():
        await record_metric(TENANT_ID, **_sample("q1", top_score=0.9, total_tokens=100))
        await record_metric(TENANT_ID, **_sample("q2", top_score=0.2, total_tokens=200))
        return await get_metrics_summary(TENANT_ID)

    summary = asyncio.run(scenario())
    assert summary["count"] == 2
    assert summary["total_tokens"] == 300
    assert summary["avg_tokens_per_query"] == 150.0
    assert summary["low_confidence_count"] == 1
    assert summary["avg_latency_ms"] == 873.1


def test_summary_is_empty_for_no_data(fake_redis):
    summary = asyncio.run(get_metrics_summary("no-data-tenant"))
    assert summary["count"] == 0
    assert summary["total_tokens"] == 0
    assert summary["low_confidence_count"] == 0
