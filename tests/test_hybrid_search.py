"""
Tests for app/rag/hybrid_search.py
Covers: BM25 indexing, bm25_search, reciprocal_rank_fusion (Issue #4)
"""

import pytest
from app.rag import hybrid_search as hs


# ---------------------------------------------------------------------------
# Helpers — reset module-level state between tests
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def reset_bm25():
    """Clear the in-memory BM25 corpus before every test."""
    hs._corpus.clear()
    hs._tokenized.clear()
    hs._bm25 = None
    yield
    hs._corpus.clear()
    hs._tokenized.clear()
    hs._bm25 = None


# ---------------------------------------------------------------------------
# add_document_to_bm25
# ---------------------------------------------------------------------------

class TestAddDocumentToBM25:
    def test_corpus_grows(self):
        hs.add_document_to_bm25("hello world")
        assert len(hs._corpus) == 1

    def test_tokenized_grows(self):
        hs.add_document_to_bm25("hello world")
        assert len(hs._tokenized) == 1
        assert hs._tokenized[0] == ["hello", "world"]

    def test_bm25_instance_created(self):
        hs.add_document_to_bm25("hello world")
        assert hs._bm25 is not None

    def test_multiple_docs(self):
        hs.add_document_to_bm25("doc one")
        hs.add_document_to_bm25("doc two")
        hs.add_document_to_bm25("doc three")
        assert len(hs._corpus) == 3


# ---------------------------------------------------------------------------
# bm25_search
# ---------------------------------------------------------------------------

class TestBM25Search:
    def test_empty_corpus_returns_empty(self):
        results = hs.bm25_search("anything")
        assert results == []

    def test_returns_list_of_tuples(self):
        hs.add_document_to_bm25("the quick brown fox")
        hs.add_document_to_bm25("lazy dog sleeps")
        results = hs.bm25_search("fox", top_k=2)
        assert isinstance(results, list)
        assert all(isinstance(r, tuple) and len(r) == 2 for r in results)

    def test_relevant_doc_ranks_first(self):
        hs.add_document_to_bm25("enterprise leave policy allows 20 days")
        hs.add_document_to_bm25("the weather is sunny today")
        hs.add_document_to_bm25("quarterly revenue report Q3")
        results = hs.bm25_search("leave policy", top_k=3)
        top_idx = results[0][0]
        assert top_idx == 0  # first doc should rank highest

    def test_top_k_limits_results(self):
        for i in range(10):
            hs.add_document_to_bm25(f"document number {i} with some content")
        results = hs.bm25_search("document", top_k=3)
        assert len(results) <= 3

    def test_scores_are_floats(self):
        hs.add_document_to_bm25("hello world test")
        results = hs.bm25_search("hello", top_k=1)
        assert isinstance(results[0][1], float)

    def test_case_insensitive(self):
        hs.add_document_to_bm25("Enterprise RAG Platform")
        results_lower = hs.bm25_search("enterprise rag", top_k=1)
        results_upper = hs.bm25_search("ENTERPRISE RAG", top_k=1)
        assert results_lower[0][0] == results_upper[0][0]


# ---------------------------------------------------------------------------
# reciprocal_rank_fusion
# ---------------------------------------------------------------------------

class TestReciprocalRankFusion:
    def _make_docs(self):
        return [
            "vector search result alpha",
            "bm25 keyword match beta",
            "shared result gamma",
            "another doc delta",
            "final doc epsilon",
        ]

    def test_returns_list_of_strings(self):
        docs = self._make_docs()
        vector_results = [docs[0], docs[2]]
        bm25_results = [(1, 2.5), (2, 1.8)]
        out = hs.reciprocal_rank_fusion(vector_results, bm25_results, docs, top_k=3)
        assert isinstance(out, list)
        assert all(isinstance(s, str) for s in out)

    def test_top_k_respected(self):
        docs = self._make_docs()
        vector_results = docs[:3]
        bm25_results = [(0, 3.0), (1, 2.0), (2, 1.0)]
        out = hs.reciprocal_rank_fusion(vector_results, bm25_results, docs, top_k=2)
        assert len(out) <= 2

    def test_shared_result_ranks_higher(self):
        """A doc appearing in both vector and BM25 results should rank above docs in only one."""
        docs = ["only in vector", "only in bm25", "in both searches"]
        vector_results = ["only in vector", "in both searches"]
        bm25_results = [(1, 5.0), (2, 4.0)]  # index 1=only in bm25, 2=in both
        out = hs.reciprocal_rank_fusion(vector_results, bm25_results, docs, top_k=3)
        assert out[0] == "in both searches"

    def test_empty_inputs_returns_empty(self):
        out = hs.reciprocal_rank_fusion([], [], [], top_k=5)
        assert out == []

    def test_alpha_zero_ignores_vector(self):
        """alpha=0 means only BM25 contributes."""
        docs = ["bm25 winner", "vector winner", "neutral"]
        vector_results = ["vector winner", "neutral"]
        bm25_results = [(0, 10.0), (2, 1.0)]  # bm25 winner at index 0
        out = hs.reciprocal_rank_fusion(
            vector_results, bm25_results, docs, top_k=3, alpha=0.0
        )
        assert out[0] == "bm25 winner"

    def test_alpha_one_ignores_bm25(self):
        """alpha=1 means only vector contributes."""
        docs = ["bm25 winner", "vector winner", "neutral"]
        vector_results = ["vector winner", "neutral"]
        bm25_results = [(0, 10.0)]  # bm25 winner
        out = hs.reciprocal_rank_fusion(
            vector_results, bm25_results, docs, top_k=3, alpha=1.0
        )
        assert out[0] == "vector winner"

    def test_out_of_bounds_bm25_index_ignored(self):
        docs = ["only doc"]
        vector_results = ["only doc"]
        bm25_results = [(999, 5.0)]  # invalid index
        out = hs.reciprocal_rank_fusion(vector_results, bm25_results, docs, top_k=1)
        assert out == ["only doc"]
