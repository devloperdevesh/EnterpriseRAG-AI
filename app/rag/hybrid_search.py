"""
Hybrid retrieval: BM25 keyword search + FAISS vector search,
fused via Reciprocal Rank Fusion (RRF).

Issue #4 — Improve Retrieval Accuracy with Hybrid Search (BM25 + Vector Search)
"""

from typing import List, Tuple
from rank_bm25 import BM25Okapi

# ---------------------------------------------------------------------------
# In-memory BM25 corpus (mirrors the FAISS documents list)
# ---------------------------------------------------------------------------

_corpus: List[str] = []          # raw document texts
_tokenized: List[List[str]] = [] # tokenized for BM25
_bm25: BM25Okapi | None = None


def _rebuild_bm25() -> None:
    global _bm25
    if _tokenized:
        _bm25 = BM25Okapi(_tokenized)
    else:
        _bm25 = None


def add_document_to_bm25(text: str) -> None:
    """Add a new document chunk to the BM25 index."""
    _corpus.append(text)
    _tokenized.append(text.lower().split())
    _rebuild_bm25()


def bm25_search(query: str, top_k: int = 10) -> List[Tuple[int, float]]:
    """
    Return (doc_index, bm25_score) pairs sorted by score descending.
    Returns empty list if corpus is empty.
    """
    if _bm25 is None or not _corpus:
        return []

    tokenized_query = query.lower().split()
    scores = _bm25.get_scores(tokenized_query)

    ranked = sorted(enumerate(scores), key=lambda x: x[1], reverse=True)
    return ranked[:top_k]


# ---------------------------------------------------------------------------
# Reciprocal Rank Fusion
# ---------------------------------------------------------------------------

def reciprocal_rank_fusion(
    vector_results: List[str],
    bm25_results: List[Tuple[int, float]],
    all_documents: List[str],
    top_k: int = 5,
    k: int = 60,
    alpha: float = 0.5,
) -> List[str]:
    """
    Fuse vector search results and BM25 results using RRF.

    Args:
        vector_results:  Ordered list of document texts from vector search.
        bm25_results:    (doc_index, score) pairs from BM25 search.
        all_documents:   Full document corpus (same order as FAISS index).
        top_k:           Number of results to return.
        k:               RRF constant (default 60).
        alpha:           Weight for vector rank score (1-alpha for BM25).

    Returns:
        Top-k document texts ranked by fused score.
    """
    scores: dict[str, float] = {}

    # Vector search contribution
    for rank, text in enumerate(vector_results):
        rrf_score = alpha * (1.0 / (k + rank + 1))
        scores[text] = scores.get(text, 0.0) + rrf_score

    # BM25 contribution
    for rank, (doc_idx, _) in enumerate(bm25_results):
        if doc_idx < len(all_documents):
            text = all_documents[doc_idx]
            rrf_score = (1 - alpha) * (1.0 / (k + rank + 1))
            scores[text] = scores.get(text, 0.0) + rrf_score

    # Sort by fused score
    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    return [text for text, _ in ranked[:top_k]]
