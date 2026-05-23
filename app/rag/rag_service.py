from app.rag.hybrid_search import hybrid_search


def answer_question(question: str) -> str:
    """
    Simple RAG answer generator
    """
    relevant_chunks = hybrid_search(question)

    if not relevant_chunks:
        return "I could not find relevant information in the documents."

    # Simple answer strategy (for now)
    context = " ".join(relevant_chunks)

    answer = f"Based on the documents, here is the answer:\n{context}"

    return answer
