from typing import Any


def _generate_query_embedding(query: str) -> list[float]:
    """Generate an embedding for a search query."""
    from app.rag.embeddings import generate_embedding

    return generate_embedding(query)


def _search_vector_index(query_embedding: list[float], top_k: int) -> list[str]:
    """Search the vector index for a query embedding."""
    from app.rag.vector_store import search_embedding

    return search_embedding(query_embedding, top_k=top_k)


def _get_bm25_index() -> tuple[Any, list[str]]:
    """Return the BM25 index and backing documents."""
    from app.rag.vector_store import get_bm25

    return get_bm25()


def _search_bm25_index(
    query: str,
    bm25: Any,
    documents: list[str],
    top_k: int,
) -> list[str]:
    """Search BM25 and omit zero-score filler documents."""
    tokens = query.lower().split()
    results = bm25.get_top_n(tokens, documents, n=top_k)

    if not hasattr(bm25, "get_scores"):
        return results

    scores = bm25.get_scores(tokens)
    matching_documents = {
        document
        for document, score in zip(documents, scores)
        if float(score) != 0.0
    }

    return [document for document in results if document in matching_documents]


def reciprocal_rank_fusion(
    vector_results: list[str],
    bm25_results: list[str],
    k: int = 60,
) -> list[str]:
    """Merge two ranked result lists with Reciprocal Rank Fusion."""
    scores: dict[str, float] = {}

    for results in (vector_results, bm25_results):
        for rank, document in enumerate(results, start=1):
            scores[document] = scores.get(document, 0.0) + 1 / (k + rank)

    return sorted(scores, key=scores.__getitem__, reverse=True)


def hybrid_search(query: str, top_k: int = 3) -> list[str]:
    """Run vector and BM25 search, then return the RRF-ranked chunks."""
    query_embedding = _generate_query_embedding(query)
    vector_results = _search_vector_index(query_embedding, top_k=10)

    bm25, documents = _get_bm25_index()
    if bm25 is None or not documents:
        return vector_results[:top_k]

    bm25_results = _search_bm25_index(query, bm25, documents, top_k=10)
    fused_results = reciprocal_rank_fusion(vector_results, bm25_results)

    return fused_results[:top_k]
