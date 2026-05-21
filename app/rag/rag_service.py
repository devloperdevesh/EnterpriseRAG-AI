from app.rag.embeddings import generate_embedding
from app.rag.vector_store import hybrid_search


def answer_question(question: str, alpha: float = 0.5) -> str:
    """
    Hybrid RAG answer generator.

    Uses BM25 + vector search fused via RRF for improved retrieval accuracy,
    especially for technical terms, abbreviations, and exact keyword matches.

    Args:
        question: The user's question.
        alpha:    Blend weight — 0.0 = pure BM25, 1.0 = pure vector, 0.5 = balanced.
    """
    query_embedding = generate_embedding(question)

    relevant_chunks = hybrid_search(
        query=question,
        query_embedding=query_embedding,
        top_k=5,
        alpha=alpha,
    )

    if not relevant_chunks:
        return "I could not find relevant information in the documents."

    context = "\n\n".join(relevant_chunks[:3])
    return f"Based on the documents:\n\n{context}"
