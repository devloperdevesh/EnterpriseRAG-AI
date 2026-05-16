import faiss
import numpy as np
from rank_bm25 import BM25Okapi
from typing import List

EMBEDDING_DIM = 384

index = faiss.IndexFlatL2(EMBEDDING_DIM)
documents: List[str] = []
corpus: List[List[str]] = []
bm25: BM25Okapi | None = None


def add_embedding(embedding: List[float], text: str) -> None:
    """Add a text chunk to the FAISS and BM25 indexes."""
    global bm25

    vector = np.array(embedding, dtype="float32").reshape(1, -1)
    index.add(vector)  # type: ignore
    documents.append(text)
    corpus.append(text.lower().split())
    bm25 = BM25Okapi(corpus)


def search_embedding(query_embedding: List[float], top_k: int = 3) -> List[str]:
    """Search the FAISS index and return matching document chunks."""
    if index.ntotal == 0:
        return []

    query_vector = np.array(query_embedding, dtype="float32").reshape(1, -1)

    distances, indices = index.search(query_vector, top_k)  # type: ignore

    results = []
    for i in indices[0]:
        if i != -1 and i < len(documents):
            results.append(documents[i])

    return results


def get_bm25() -> tuple[BM25Okapi | None, List[str]]:
    """Return the current BM25 index and its backing documents."""
    return bm25, documents
