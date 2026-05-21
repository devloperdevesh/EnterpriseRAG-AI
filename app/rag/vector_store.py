import faiss
import numpy as np
from typing import List

from app.rag.hybrid_search import (
    add_document_to_bm25,
    bm25_search,
    reciprocal_rank_fusion,
)

EMBEDDING_DIM = 384

index = faiss.IndexFlatL2(EMBEDDING_DIM)
documents: List[str] = []


def add_embedding(embedding: List[float], text: str) -> None:
    """Add a vector embedding + raw text to both FAISS and BM25 indexes."""
    vector = np.array(embedding, dtype="float32").reshape(1, -1)
    index.add(vector)  # type: ignore
    documents.append(text)
    add_document_to_bm25(text)


def search_embedding(query_embedding: List[float], top_k: int = 3) -> List[str]:
    """Pure vector (FAISS) search — kept for backward compatibility."""
    if index.ntotal == 0:
        return []

    query_vector = np.array(query_embedding, dtype="float32").reshape(1, -1)
    distances, indices = index.search(query_vector, top_k)  # type: ignore

    results = []
    for i in indices[0]:
        if i != -1 and i < len(documents):
            results.append(documents[i])
    return results


def hybrid_search(
    query: str,
    query_embedding: List[float],
    top_k: int = 5,
    alpha: float = 0.5,
) -> List[str]:
    """
    Hybrid BM25 + vector search fused with Reciprocal Rank Fusion.

    Args:
        query:           Raw query string (for BM25).
        query_embedding: Dense embedding of the query (for FAISS).
        top_k:           Number of results to return.
        alpha:           Weight for vector results (0=pure BM25, 1=pure vector).

    Returns:
        Top-k document texts ranked by fused score.
    """
    if index.ntotal == 0:
        return []

    # --- Vector search (fetch more candidates for fusion) ---
    fetch_k = min(top_k * 3, index.ntotal)
    query_vector = np.array(query_embedding, dtype="float32").reshape(1, -1)
    _, indices = index.search(query_vector, fetch_k)  # type: ignore
    vector_results = [
        documents[i] for i in indices[0] if i != -1 and i < len(documents)
    ]

    # --- BM25 search ---
    bm25_results = bm25_search(query, top_k=fetch_k)

    # --- Fuse ---
    return reciprocal_rank_fusion(
        vector_results=vector_results,
        bm25_results=bm25_results,
        all_documents=documents,
        top_k=top_k,
        alpha=alpha,
    )
