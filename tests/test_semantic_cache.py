"""Tests for semantic query cache layer (Issue #161)."""

import asyncio
import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.rag.semantic_cache import (
    SIMILARITY_THRESHOLD,
    _cache_key,
    _cache_metadata_key,
    _cosine_similarity,
    cache_response,
    clear_user_cache,
    get_cache_stats,
    get_cached_response,
)


class TestCosineSimilarity:
    """Tests for cosine similarity calculation."""

    def test_identical_vectors(self):
        """Identical vectors should have similarity of 1.0."""
        vec = [1.0, 2.0, 3.0]
        similarity = _cosine_similarity(vec, vec)
        assert similarity == pytest.approx(1.0, rel=1e-5)

    def test_orthogonal_vectors(self):
        """Orthogonal vectors should have similarity of 0.0."""
        vec1 = [1.0, 0.0]
        vec2 = [0.0, 1.0]
        similarity = _cosine_similarity(vec1, vec2)
        assert similarity == pytest.approx(0.0, abs=1e-5)

    def test_opposite_vectors(self):
        """Opposite vectors should have similarity of -1.0."""
        vec1 = [1.0, 2.0]
        vec2 = [-1.0, -2.0]
        similarity = _cosine_similarity(vec1, vec2)
        assert similarity == pytest.approx(-1.0, rel=1e-5)

    def test_zero_vector(self):
        """Zero vector should have similarity of 0.0."""
        vec1 = [0.0, 0.0]
        vec2 = [1.0, 2.0]
        similarity = _cosine_similarity(vec1, vec2)
        assert similarity == 0.0


class TestCacheKeyGeneration:
    """Tests for cache key generation."""

    def test_cache_key_format(self):
        """Cache key should follow expected format."""
        user_id = "user123"
        key = _cache_key(user_id)
        assert key == f"semantic_cache:user:{user_id}"

    def test_metadata_key_format(self):
        """Metadata key should follow expected format."""
        user_id = "user123"
        key = _cache_metadata_key(user_id)
        assert key == f"semantic_cache:metadata:{user_id}"


class TestGetCachedResponse:
    """Tests for retrieving cached responses."""

    @pytest.mark.asyncio
    async def test_no_cached_entries(self):
        """Should return None if no cached entries exist."""
        with patch("app.rag.semantic_cache.get_redis") as mock_redis_factory:
            mock_redis = AsyncMock()
            mock_redis.hgetall = AsyncMock(return_value={})
            mock_redis_factory.return_value = mock_redis

            with patch("app.rag.semantic_cache.generate_embedding") as mock_embedding:
                mock_embedding.return_value = [1.0, 0.0, 0.0]

                result = await get_cached_response("user123", "test query")
                assert result is None

    @pytest.mark.asyncio
    async def test_exact_match_cache_hit(self):
        """Should return cached response for identical query embedding."""
        query_embedding = [1.0, 0.0, 0.0]
        cached_entry = {
            "query": "test query",
            "embedding": query_embedding,
            "answer": "test answer",
            "chunks": [{"text": "chunk1"}],
            "source_documents": ["doc1.pdf"],
            "cached_at": 1234567890,
        }

        with patch("app.rag.semantic_cache.get_redis") as mock_redis_factory:
            mock_redis = AsyncMock()
            mock_redis.hgetall = AsyncMock(
                return_value={"entry1": json.dumps(cached_entry)}
            )
            mock_redis_factory.return_value = mock_redis

            with patch("app.rag.semantic_cache.generate_embedding") as mock_embedding:
                mock_embedding.return_value = query_embedding

                with patch("app.rag.semantic_cache._record_cache_hit"):
                    result = await get_cached_response("user123", "test query")

                    assert result is not None
                    assert result["answer"] == "test answer"
                    assert result["from_cache"] is True
                    assert result["similarity_score"] == pytest.approx(1.0)

    @pytest.mark.asyncio
    async def test_similarity_below_threshold(self):
        """Should return None if similarity is below threshold."""
        with patch("app.rag.semantic_cache.get_redis") as mock_redis_factory:
            mock_redis = AsyncMock()
            cached_entry = {
                "query": "original query",
                "embedding": [1.0, 0.0, 0.0],
                "answer": "test answer",
                "chunks": [],
                "source_documents": [],
                "cached_at": 1234567890,
            }
            mock_redis.hgetall = AsyncMock(
                return_value={"entry1": json.dumps(cached_entry)}
            )
            mock_redis_factory.return_value = mock_redis

            with patch("app.rag.semantic_cache.generate_embedding") as mock_embedding:
                # Use orthogonal vector (similarity = 0.0)
                mock_embedding.return_value = [0.0, 1.0, 0.0]

                result = await get_cached_response("user123", "completely different query")
                assert result is None

    @pytest.mark.asyncio
    async def test_redis_timeout_graceful_failure(self):
        """Should gracefully handle Redis timeout."""
        with patch("app.rag.semantic_cache.get_redis") as mock_redis_factory:
            mock_redis = AsyncMock()
            mock_redis.hgetall = AsyncMock(
                side_effect=asyncio.TimeoutError()
            )
            mock_redis_factory.return_value = mock_redis

            with patch("app.rag.semantic_cache.generate_embedding") as mock_embedding:
                mock_embedding.return_value = [1.0, 0.0, 0.0]

                result = await get_cached_response("user123", "test query")
                assert result is None


class TestCacheResponse:
    """Tests for storing cached responses."""

    @pytest.mark.asyncio
    async def test_successful_cache_write(self):
        """Should successfully cache a response."""
        with patch("app.rag.semantic_cache.get_redis") as mock_redis_factory:
            mock_redis = AsyncMock()
            mock_redis.hset = AsyncMock(return_value=1)
            mock_redis.expire = AsyncMock(return_value=True)
            mock_redis.hlen = AsyncMock(return_value=1)
            mock_redis_factory.return_value = mock_redis

            with patch("app.rag.semantic_cache.generate_embedding") as mock_embedding:
                mock_embedding.return_value = [1.0, 0.0, 0.0]

                result = await cache_response(
                    "user123",
                    "test query",
                    "test answer",
                    [{"text": "chunk1"}],
                    ["doc1.pdf"],
                )

                assert result is True
                mock_redis.hset.assert_called_once()
                mock_redis.expire.assert_called_once()

    @pytest.mark.asyncio
    async def test_cache_with_no_embedding(self):
        """Should return False if embedding generation fails."""
        with patch("app.rag.semantic_cache.generate_embedding") as mock_embedding:
            mock_embedding.return_value = None

            result = await cache_response(
                "user123",
                "test query",
                "test answer",
                [],
                [],
            )

            assert result is False


class TestClearUserCache:
    """Tests for clearing user cache."""

    @pytest.mark.asyncio
    async def test_successful_cache_clear(self):
        """Should successfully clear user cache."""
        with patch("app.rag.semantic_cache.get_redis") as mock_redis_factory:
            mock_redis = AsyncMock()
            mock_redis.delete = AsyncMock(return_value=2)
            mock_redis_factory.return_value = mock_redis

            result = await clear_user_cache("user123")

            assert result is True
            mock_redis.delete.assert_called_once()

    @pytest.mark.asyncio
    async def test_clear_cache_redis_error(self):
        """Should gracefully handle Redis errors during clear."""
        with patch("app.rag.semantic_cache.get_redis") as mock_redis_factory:
            mock_redis = AsyncMock()
            mock_redis.delete = AsyncMock(side_effect=Exception("Redis error"))
            mock_redis_factory.return_value = mock_redis

            result = await clear_user_cache("user123")

            assert result is False


class TestCacheStats:
    """Tests for cache statistics."""

    @pytest.mark.asyncio
    async def test_get_cache_stats(self):
        """Should retrieve cache statistics correctly."""
        with patch("app.rag.semantic_cache.get_redis") as mock_redis_factory:
            mock_redis = AsyncMock()
            mock_redis.hlen = AsyncMock(return_value=5)
            mock_redis.hgetall = AsyncMock(return_value={"cache_hits": "10"})
            mock_redis_factory.return_value = mock_redis

            stats = await get_cache_stats("user123")

            assert stats["cached_queries"] == 5
            assert stats["cache_hits"] == 10
            assert stats["hit_rate"] == pytest.approx(10 / 15)

    @pytest.mark.asyncio
    async def test_cache_stats_redis_error(self):
        """Should return zeros on Redis error."""
        with patch("app.rag.semantic_cache.get_redis") as mock_redis_factory:
            mock_redis = AsyncMock()
            mock_redis.hlen = AsyncMock(side_effect=Exception("Redis error"))
            mock_redis_factory.return_value = mock_redis

            stats = await get_cache_stats("user123")

            assert stats["cached_queries"] == 0
            assert stats["cache_hits"] == 0
            assert stats["hit_rate"] == 0
