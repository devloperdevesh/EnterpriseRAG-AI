import faiss
import numpy as np

from typing import List, Dict, Any

EMBEDDING_DIM = 384

index = faiss.IndexFlatL2(EMBEDDING_DIM)

# ======================================
# Tenant-aware metadata store
# ======================================

documents: List[Dict[str, Any]] = []


def add_embedding(
    embedding: List[float],
    text: str,
    tenant_id: str
):

    vector = np.array(
        embedding,
        dtype="float32"
    ).reshape(1, -1)

    index.add(vector)  # type: ignore

    documents.append({
        "tenant_id": tenant_id,
        "text": text
    })


def search_embedding(
    query_embedding: List[float],
    tenant_id: str,
    top_k: int = 3
):

    if index.ntotal == 0:
        return []

    query_vector = np.array(
        query_embedding,
        dtype="float32"
    ).reshape(1, -1)

    distances, indices = index.search(
        query_vector,
        top_k
    )  # type: ignore

    results = []

    for i in indices[0]:

        if i == -1:
            continue

        if i >= len(documents):
            continue

        document = documents[i]

        # ======================================
        # Tenant isolation enforcement
        # ======================================

        if document["tenant_id"] != tenant_id:
            continue

        results.append(
            document["text"]
        )

    return results