import threading
from typing import List, Optional, TypedDict

import faiss
import numpy as np

EMBEDDING_DIM = 384

index = faiss.IndexFlatL2(EMBEDDING_DIM)
documents: List[str] = []
# Parallel to `documents`: the source file each chunk came from (may be "").
sources: List[str] = []

# The FAISS index and the parallel `documents`/`sources` lists are shared
# mutable state. Writes (document ingestion runs in a FastAPI background
# thread) and reads (the query path runs search via `asyncio.to_thread`) can
# happen concurrently, so every access is serialised through this lock to keep
# the index and the lists consistent with each other.
_index_lock = threading.Lock()

# Maximum L2 distance for a result to be considered relevant.
# Chunks whose distance exceeds this threshold are filtered out before they
# are passed to the LLM. Tune based on your embedding model and corpus.
# A distance of 0.0 means identical vectors; higher values mean less similar.
DEFAULT_RELEVANCE_THRESHOLD: float = 1.5


class ScoredChunk(TypedDict):
    text: str
    score: float  # cosine-similarity-like score in [0, 1], higher is better
    source: str
    distance: float  # raw L2 distance from FAISS (lower is better)


def add_embedding(embedding: List[float], text: str, source: Optional[str] = None):
    vector = np.array(embedding, dtype="float32").reshape(1, -1)
    with _index_lock:
        index.add(vector)  # type: ignore
        documents.append(text)
        sources.append(source or "")


def search_embedding(
    query_embedding: List[float],
    top_k: int = 5,
    relevance_threshold: float = DEFAULT_RELEVANCE_THRESHOLD,
) -> List[ScoredChunk]:
    """Return the top-k most relevant chunks, ranked by relevance score.

    Results are sorted from most relevant (highest score) to least relevant.
    Chunks whose L2 distance exceeds ``relevance_threshold`` are filtered out
    so that out-of-domain or low-confidence results are never returned.

    Args:
        query_embedding: The embedding vector for the user's query.
        top_k: Maximum number of results to return before threshold filtering.
        relevance_threshold: Maximum L2 distance allowed. Results with a higher
            distance are considered out-of-domain and are excluded.

    Returns:
        A list of :class:`ScoredChunk` dicts sorted descending by ``score``.
        Returns an empty list when the vector store is empty.
    """
    with _index_lock:
        n = index.ntotal
        if n == 0:
            return []

        # Cap top_k at the number of indexed vectors to avoid FAISS errors.
        k = min(top_k, n)
        query_vector = np.array(query_embedding, dtype="float32").reshape(1, -1)
        distances, indices = index.search(query_vector, k)  # type: ignore

        results: List[ScoredChunk] = []
        for dist, idx in zip(distances[0], indices[0]):
            if idx < 0:
                # FAISS returns -1 for empty slots when k > n.
                continue

            # Apply the relevance threshold: filter out low-confidence results.
            if dist > relevance_threshold:
                continue

            # Convert L2 distance to a normalised relevance score in [0, 1].
            # score = 1 / (1 + distance) so that distance 0 → score 1.0 and
            # higher distances approach 0 without going negative.
            score = 1.0 / (1.0 + float(dist))

            results.append(
                ScoredChunk(
                    text=documents[idx],
                    score=round(score, 4),
                    source=sources[idx],
                    distance=round(float(dist), 4),
                )
            )

        # Sort descending by relevance score (most relevant first).
        results.sort(key=lambda c: c["score"], reverse=True)
        return results
