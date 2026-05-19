import faiss
import numpy as np
from typing import List

EMBEDDING_DIM = 384

index = faiss.IndexFlatL2(EMBEDDING_DIM)
documents: List[str] = []

def add_embedding(embedding: List[float], text: str) -> None:
    """
    Adds a document embedding and its corresponding text to the FAISS index.

    Args:
        embedding (List[float]): A list of floats representing the dense vector embedding of the document.
        text (str): The raw text content of the document being embedded.
    """
    vector = np.array(embedding, dtype="float32").reshape(1, -1)
    index.add(vector) # type: ignore
    documents.append(text)

def search_embedding(query_embedding: List[float], top_k: int = 3) -> List[str]:
    """
    Searches the FAISS index for the most similar document embeddings to a given query.

    Args:
        query_embedding (List[float]): The dense vector embedding of the search query.
        top_k (int, optional): The number of top matching documents to return. Defaults to 3.

    Returns:
        List[str]: A list of the raw text strings of the top_k most similar documents.
                   Returns an empty list if the FAISS index is empty.
    """
    if index.ntotal == 0:
        return []

    query_vector = np.array(query_embedding, dtype="float32").reshape(1, -1)

    distances, indices = index.search(query_vector, top_k)  # type: ignore

    results = []
    for i in indices[0]:
        if i != -1 and i < len(documents):
            results.append(documents[i])

    return results
