from typing import Any


class FakeBm25:
    """Small BM25 double that exposes ranked results and raw scores."""

    def get_scores(self, _tokens: list[str]) -> list[float]:
        """Return one zero keyword score and one positive keyword score."""
        return [0.0, 2.0]

    def get_top_n(self, _tokens: list[str], documents: list[str], n: int) -> list[str]:
        """Return BM25 results including a zero-score filler document."""
        return [documents[1], documents[0]][:n]


def test_rrf_prioritizes_documents_present_in_both_rankings() -> None:
    from app.rag.hybrid_search import reciprocal_rank_fusion

    vector_results = ["leave policy", "refund policy"]
    bm25_results = ["refund policy", "security policy"]

    results = reciprocal_rank_fusion(vector_results, bm25_results)

    assert results[0] == "refund policy"


def test_rrf_includes_documents_from_disjoint_rankings() -> None:
    from app.rag.hybrid_search import reciprocal_rank_fusion

    vector_results = ["paid leave", "remote work"]
    bm25_results = ["refund policy", "security policy"]

    results = reciprocal_rank_fusion(vector_results, bm25_results)

    assert set(results) == set(vector_results + bm25_results)


def test_hybrid_search_returns_empty_list_for_empty_index(monkeypatch: Any) -> None:
    from app.rag import hybrid_search

    monkeypatch.setattr(
        hybrid_search,
        "_generate_query_embedding",
        lambda _query: [0.0] * 384,
    )
    monkeypatch.setattr(
        hybrid_search,
        "_search_vector_index",
        lambda _embedding, top_k: [],
    )
    monkeypatch.setattr(hybrid_search, "_get_bm25_index", lambda: (None, []))

    assert hybrid_search.hybrid_search("refund policy") == []


def test_hybrid_search_does_not_boost_zero_score_bm25_results(
    monkeypatch: Any,
) -> None:
    from app.rag import hybrid_search

    documents = ["leave policy", "refund policy"]

    monkeypatch.setattr(
        hybrid_search,
        "_generate_query_embedding",
        lambda _query: [0.0] * 384,
    )
    monkeypatch.setattr(
        hybrid_search,
        "_search_vector_index",
        lambda _embedding, top_k: ["leave policy", "refund policy"],
    )
    monkeypatch.setattr(
        hybrid_search,
        "_get_bm25_index",
        lambda: (FakeBm25(), documents),
    )

    assert hybrid_search.hybrid_search("refund policy", top_k=1) == ["refund policy"]
