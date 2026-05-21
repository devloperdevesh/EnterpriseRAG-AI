"""
Tests for app/rag/vector_store.py
Covers: add_embedding, search_embedding (pure vector), hybrid_search
"""

import pytest
import numpy as np
from app.rag import vector_store as vs
from app.rag import hybrid_search as hs


# ---------------------------------------------------------------------------
# Reset shared in-memory state between tests
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def reset_stores():
    """Reset FAISS index and BM25 corpus before each test."""
    import faiss
    vs.index = faiss.IndexFlatL2(vs.EMBEDDING_DIM)
    vs.documents.clear()
    hs._corpus.clear()
    hs._tokenized.clear()
    hs._bm25 = None
    yield
    vs.index = faiss.IndexFlatL2(vs.EMBEDDING_DIM)
    vs.documents.clear()
    hs._corpus.clear()
    hs._tokenized.clear()
    hs._bm25 = None


def _random_embedding(seed: int = 0) -> list:
    rng = np.random.default_rng(seed)
    return rng.random(vs.EMBEDDING_DIM).tolist()


# ---------------------------------------------------------------------------
# add_embedding
# ---------------------------------------------------------------------------

class TestAddEmbedding:
    def test_faiss_index_grows(self):
        vs.add_embedding(_random_embedding(0), "doc one")
        assert vs.index.ntotal == 1

    def test_documents_list_grows(self):
        vs.add_embedding(_random_embedding(0), "doc one")
        assert len(vs.documents) == 1
        assert vs.documents[0] == "doc one"

    def test_bm25_corpus_grows(self):
        vs.add_embedding(_random_embedding(0), "doc one")
        assert len(hs._corpus) == 1

    def test_multiple_adds(self):
        for i in range(5):
            vs.add_embedding(_random_embedding(i), f"document {i}")
        assert vs.index.ntotal == 5
        assert len(vs.documents) == 5
        assert len(hs._corpus) == 5


# ---------------------------------------------------------------------------
# search_embedding (pure vector)
# ---------------------------------------------------------------------------

class TestSearchEmbedding:
    def test_empty_index_returns_empty(self):
        result = vs.search_embedding(_random_embedding(0))
        assert result == []

    def test_returns_list_of_strings(self):
        vs.add_embedding(_random_embedding(0), "hello world")
        result = vs.search_embedding(_random_embedding(0))
        assert isinstance(result, list)
        assert all(isinstance(r, str) for r in result)

    def test_exact_match_ranks_first(self):
        """Adding a vector and searching with the same vector should return that doc first."""
        emb = _random_embedding(42)
        vs.add_embedding(emb, "target document")
        vs.add_embedding(_random_embedding(1), "noise doc one")
        vs.add_embedding(_random_embedding(2), "noise doc two")
        result = vs.search_embedding(emb, top_k=1)
        assert result[0] == "target document"

    def test_top_k_limits_results(self):
        for i in range(10):
            vs.add_embedding(_random_embedding(i), f"doc {i}")
        result = vs.search_embedding(_random_embedding(99), top_k=3)
        assert len(result) <= 3


# ---------------------------------------------------------------------------
# hybrid_search
# ---------------------------------------------------------------------------

class TestHybridSearch:
    def test_empty_index_returns_empty(self):
        result = vs.hybrid_search("anything", _random_embedding(0))
        assert result == []

    def test_returns_list_of_strings(self):
        vs.add_embedding(_random_embedding(0), "enterprise leave policy")
        result = vs.hybrid_search("leave policy", _random_embedding(0))
        assert isinstance(result, list)
        assert all(isinstance(r, str) for r in result)

    def test_keyword_match_surfaces_correct_doc(self):
        """BM25 should help surface the doc with exact keyword match."""
        emb_policy = _random_embedding(10)
        emb_noise1 = _random_embedding(11)
        emb_noise2 = _random_embedding(12)

        vs.add_embedding(emb_policy, "company allows 20 days paid leave policy")
        vs.add_embedding(emb_noise1, "quarterly revenue report financial summary")
        vs.add_embedding(emb_noise2, "software architecture microservices design")

        # Query embedding is random (not close to any doc) — BM25 should still find it
        results = vs.hybrid_search(
            query="leave policy",
            query_embedding=_random_embedding(99),
            top_k=3,
            alpha=0.3,  # lean on BM25
        )
        assert "company allows 20 days paid leave policy" in results

    def test_top_k_respected(self):
        for i in range(10):
            vs.add_embedding(_random_embedding(i), f"document about topic {i}")
        results = vs.hybrid_search("topic", _random_embedding(99), top_k=4)
        assert len(results) <= 4

    def test_alpha_one_behaves_like_vector_search(self):
        """With alpha=1, hybrid_search should return same results as pure vector search."""
        emb = _random_embedding(42)
        vs.add_embedding(emb, "target")
        vs.add_embedding(_random_embedding(1), "noise")

        vector_only = vs.search_embedding(emb, top_k=2)
        hybrid = vs.hybrid_search("target", emb, top_k=2, alpha=1.0)

        # Both should have "target" as first result
        assert vector_only[0] == hybrid[0]
