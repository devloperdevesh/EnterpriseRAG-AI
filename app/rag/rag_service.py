from app.rag.embeddings import generate_embedding
from app.rag.vector_store import search_embedding_scored
from app.rag.reranker import rerank_chunks

def answer_question(question: str) -> str:
    """
    RAG answer generator with reranking + multi-chunk context
    """
    query_embedding = generate_embedding(question)

    # Fetch top 10 candidates from FAISS
    candidate_chunks = search_embedding_scored(query_embedding, top_k=10)

    if not candidate_chunks:
        return "I could not find relevant information in the documents."

    # Rerank and keep top 3
    top_chunks = rerank_chunks(question, candidate_chunks, top_n=3)

    # Build context with source attribution
    context_parts = []
    for i, chunk in enumerate(top_chunks, 1):
        source = chunk.get("source", "unknown")
        context_parts.append(f"[Source {i}: {source}]\n{chunk['text']}")

    context = "\n\n---\n\n".join(context_parts)

    answer = f"Based on the documents, here is the answer:\n{context}"

    return answer
