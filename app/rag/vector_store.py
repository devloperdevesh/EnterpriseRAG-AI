import faiss
import numpy as np
from typing import List

EMBEDDING_DIM = 384

index = faiss.IndexFlatL2(EMBEDDING_DIM)
documents: List[str] = []

def add_embedding(embedding: List[float], text: str):
    vector = np.array(embedding, dtype="float32").reshape(1, -1)
    index.add(vector) # type: ignore
    documents.append(text)

def search_embedding(query_embedding: List[float], top_k: int = 3):
    if index.ntotal == 0:
        return []

    query_vector = np.array(query_embedding, dtype="float32").reshape(1, -1)

    distances, indices = index.search(query_vector, top_k)  # type: ignore

    results = []
    for i in indices[0]:
        if i != -1 and i < len(documents):
            results.append(documents[i])

    return results
