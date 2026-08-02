"""
app/retrieval/vector_store.py

FAISS-based vector similarity search — exposed as a FastAPI dependency.

Architecture note: FAISS accepts only NumPy float32 arrays. The conversion
from Apache Arrow RecordBatch → np.array() at this boundary is intentional
(see docs/ADR-001-faiss-vector-backend.md). This is the sole zero-copy
exception in the pipeline; all other stages remain Arrow-native.
"""

import numpy as np
import faiss
from functools import lru_cache
from typing import Tuple


class VectorStore:
    """Wraps a FAISS IndexFlatL2 for semantic retrieval."""

    def __init__(self, dimension: int = 384):
        self.dimension = dimension
        self.index = faiss.IndexFlatL2(dimension)
        self.documents: list[str] = []

    def add(self, embeddings: np.ndarray, documents: list[str]) -> None:
        """
        Add embeddings to the index.
        embeddings: np.ndarray of shape (n, dimension), dtype float32
        """
        assert embeddings.dtype == np.float32, "FAISS requires float32"
        self.index.add(embeddings)
        self.documents.extend(documents)

    def search(
        self, query_embedding: np.ndarray, top_k: int = 5
    ) -> Tuple[list[str], list[float]]:
        """
        Search for top_k nearest neighbours.
        query_embedding: np.ndarray of shape (1, dimension), dtype float32
        Returns: (documents, distances)
        """
        assert query_embedding.dtype == np.float32, "FAISS requires float32"
        distances, indices = self.index.search(query_embedding, top_k)
        results = [
            self.documents[i] for i in indices[0] if i < len(self.documents)
        ]
        return results, distances[0].tolist()

    @property
    def total_vectors(self) -> int:
        return self.index.ntotal


@lru_cache(maxsize=1)
def get_vector_store() -> VectorStore:
    """
    FastAPI dependency: returns the singleton VectorStore instance.

    Usage in a route:
        from fastapi import Depends
        from app.retrieval.vector_store import VectorStore, get_vector_store

        @router.post("/query")
        async def query(store: VectorStore = Depends(get_vector_store)):
            results, _ = store.search(embedding, top_k=5)
    """
    return VectorStore()