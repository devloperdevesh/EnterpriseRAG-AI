from typing import Optional

from app.rag.embeddings import generate_embedding
from app.rag.vector_store import ScoredChunk, search_embedding

# Minimum relevance score [0, 1] for a chunk to be included in the LLM prompt.
# Chunks below this threshold are discarded to prevent hallucination from
# out-of-domain or weakly-matched context.
MIN_SCORE_THRESHOLD: float = 0.4

# Fallback message returned when no relevant context is found.
_OUT_OF_DOMAIN_RESPONSE = (
    "I could not find relevant information in the knowledge base to answer your "
    "question. Please refine your query or upload documents that cover this topic."
)


def answer_question(
    question: str,
    top_k: int = 5,
    min_score: float = MIN_SCORE_THRESHOLD,
    relevance_threshold: Optional[float] = None,
) -> str:
    """
    RAG answer generator with relevance-ranked retrieval and out-of-domain detection.

    Embeds the user question, retrieves the top-k most relevant chunks from the
    vector store (sorted by descending relevance score), filters out chunks below
    ``min_score``, and falls back to a clear out-of-domain response when no
    sufficiently relevant context exists.

    Args:
        question: The user's natural-language question.
        top_k: Maximum number of candidate chunks to retrieve from the vector store.
        min_score: Minimum relevance score [0, 1] a chunk must achieve to be used.
            Chunks below this value are discarded before the prompt is assembled.
        relevance_threshold: Maximum L2 distance forwarded to the vector store.
            If None, the vector store's default threshold is used.

    Returns:
        The LLM-generated answer string, or the out-of-domain fallback message.
    """
    query_embedding = generate_embedding(question)

    kwargs = {"top_k": top_k}
    if relevance_threshold is not None:
        kwargs["relevance_threshold"] = relevance_threshold

    scored_chunks: list[ScoredChunk] = search_embedding(query_embedding, **kwargs)

    # Filter by minimum relevance score.
    relevant_chunks = [c for c in scored_chunks if c["score"] >= min_score]

    if not relevant_chunks:
        return _OUT_OF_DOMAIN_RESPONSE

    # Build a ranked context block, annotated with source and confidence.
    context_parts = []
    for i, chunk in enumerate(relevant_chunks, start=1):
        source_info = f" [{chunk['source']}]" if chunk["source"] else ""
        score_info = f" (relevance: {chunk['score']:.2f})"
        context_parts.append(f"[{i}]{source_info}{score_info}\n{chunk['text']}")

    context = "\n\n".join(context_parts)

    from app.rag.llm import generate_answer  # local import to avoid circular deps

    return generate_answer(question=question, context=context)
