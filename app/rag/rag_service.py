from app.rag.embeddings import generate_embedding
from app.rag.vector_store import search_embedding


def answer_question(question: str) -> str:
    """
    Simple RAG answer generator
    """
    query_embedding = generate_embedding(question)

    relevant_chunks = search_embedding(query_embedding)

    if not relevant_chunks:
        return "I could not find relevant information in the documents."

    # Simple answer strategy (for now)
    context = " ".join(relevant_chunks)

    answer = f"Based on the documents, here is the answer:\n{context}"

    return answer
