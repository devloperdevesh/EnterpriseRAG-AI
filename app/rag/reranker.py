from sentence_transformers import CrossEncoder
from typing import List
from app.rag.vector_store import ScoredChunk

_reranker = None

def get_reranker() -> CrossEncoder:
    global _reranker
    if _reranker is None:
        _reranker = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")
    return _reranker

def rerank_chunks(query: str, chunks: List[ScoredChunk], top_n: int = 3) -> List[ScoredChunk]:
    if not chunks:
        return []
    reranker = get_reranker()
    pairs = [[query, chunk["text"]] for chunk in chunks]
    scores = reranker.predict(pairs)
    ranked = sorted(zip(scores, chunks), key=lambda x: x[0], reverse=True)
    return [chunk for _, chunk in ranked[:top_n]]
