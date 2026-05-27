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


class ScoredChunk(TypedDict):
    text: str
    score: float
    source: str


def add_embedding(embedding: List[float], text: str, source: Optional[str] = None):
    vector = np.array(embedding, dtype="float32").reshape(1, -1)
    with _index_lock:
        index.add(vector)  # type: ignore
        documents.append(text)
        sources.append(source or "")


def search_embedding(query_embedding: List[float], top_k: int = 3) -> List[str]:
    """Return the raw text of the ``top_k`` most similar chunks (legacy shape)."""
    return [chunk["text"] for chunk in search_embedding_scored(query_embedding, top_k)]


def search_embedding_scored(
    query_embedding: List[float], top_k: int = 3
) -> List[ScoredChunk]:
    """Return the ``top_k`` most similar chunks with similarity score and source.

    The FAISS ``IndexFlatL2`` returns squared L2 distances (lower = closer). We
    convert each to a bounded similarity score in ``(0, 1]`` via
    ``1 / (1 + distance)`` so the frontend can display an intuitive
    "higher = more relevant" number without exposing raw distances.
    """
    query_vector = np.array(query_embedding, dtype="float32").reshape(1, -1)

    # Hold the lock for the whole search: the index query and the subsequent
    # reads of `documents`/`sources` must see a consistent snapshot.
    with _index_lock:
        if index.ntotal == 0:
            return []

        distances, indices = index.search(query_vector, top_k)  # type: ignore

        results: List[ScoredChunk] = []
        for distance, i in zip(distances[0], indices[0]):
            if i == -1 or i >= len(documents):
                continue
            results.append(
                {
                    "text": documents[i],
                    "score": round(1.0 / (1.0 + float(distance)), 4),
                    "source": sources[i] if i < len(sources) else "",
                }
            )
    return results
