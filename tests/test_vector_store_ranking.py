"""Tests for relevance-score ranking and out-of-domain filtering.

These tests are isolated from external services: they seed the in-memory FAISS
index directly and verify the sorting and threshold logic.
"""

import pytest

from app.rag import vector_store as vs


def _reset_store():
    """Reset the global FAISS index and document lists between tests."""
    import faiss

    vs.index = faiss.IndexFlatL2(vs.EMBEDDING_DIM)
    vs.documents.clear()
    vs.sources.clear()


@pytest.fixture(autouse=True)
def clean_store():
    _reset_store()
    yield
    _reset_store()


def _unit_vec(dim: int, hot_index: int) -> list[float]:
    """Return a unit vector with 1.0 at `hot_index` and 0.0 elsewhere."""
    v = [0.0] * dim
    v[hot_index] = 1.0
    return v


def test_empty_store_returns_empty_list():
    result = vs.search_embedding(_unit_vec(vs.EMBEDDING_DIM, 0))
    assert result == []


def test_results_sorted_by_score_descending():
    """Chunks should be returned most-relevant-first."""
    # Add two chunks: one close to the query vector, one further away.
    close_vec = _unit_vec(vs.EMBEDDING_DIM, 0)   # distance ~ 0 from query
    far_vec = _unit_vec(vs.EMBEDDING_DIM, 1)      # distance ~ 1.41 from query

    vs.add_embedding(close_vec, "close chunk", source="docA")
    vs.add_embedding(far_vec, "far chunk", source="docB")

    query = _unit_vec(vs.EMBEDDING_DIM, 0)
    results = vs.search_embedding(query, top_k=5, relevance_threshold=10.0)

    assert len(results) == 2
    assert results[0]["text"] == "close chunk"
    assert results[1]["text"] == "far chunk"
    # Scores must be in descending order.
    assert results[0]["score"] >= results[1]["score"]


def test_threshold_filters_distant_chunks():
    """Chunks beyond the relevance threshold should be excluded."""
    close_vec = _unit_vec(vs.EMBEDDING_DIM, 0)
    far_vec = _unit_vec(vs.EMBEDDING_DIM, 1)   # L2 distance ≈ 1.414 from query

    vs.add_embedding(close_vec, "close chunk", source="docA")
    vs.add_embedding(far_vec, "far chunk", source="docB")

    query = _unit_vec(vs.EMBEDDING_DIM, 0)
    # Tight threshold: only the identical vector should pass.
    results = vs.search_embedding(query, top_k=5, relevance_threshold=0.01)

    assert len(results) == 1
    assert results[0]["text"] == "close chunk"


def test_scored_chunk_has_expected_keys():
    vec = _unit_vec(vs.EMBEDDING_DIM, 0)
    vs.add_embedding(vec, "test chunk", source="src")

    results = vs.search_embedding(vec, top_k=1)
    assert len(results) == 1
    chunk = results[0]
    assert "text" in chunk
    assert "score" in chunk
    assert "source" in chunk
    assert "distance" in chunk
    assert 0.0 <= chunk["score"] <= 1.0
    assert chunk["distance"] >= 0.0
