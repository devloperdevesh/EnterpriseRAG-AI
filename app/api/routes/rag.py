from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import asyncio

from app.core.dependencies import get_current_user
from app.rag.embeddings import generate_embedding
from app.rag.vector_store import hybrid_search
from app.rag.llm import generate_answer

router = APIRouter(prefix="/rag", tags=["rag"])


class RAGQuery(BaseModel):
    question: str
    alpha: float = 0.5  # 0 = pure BM25, 1 = pure vector, 0.5 = balanced


@router.post("/query/stream")
async def stream_query(data: RAGQuery, user=Depends(get_current_user)):
    """
    Hybrid RAG query endpoint.
    Combines BM25 keyword search + FAISS vector search via RRF,
    then streams the LLM answer token by token.
    """
    question = data.question

    # Generate dense embedding for vector search
    query_emb = generate_embedding(question)

    # Hybrid retrieval (BM25 + vector, fused via RRF)
    results = hybrid_search(
        query=question,
        query_embedding=query_emb,
        top_k=5,
        alpha=data.alpha,
    )

    async def event_stream():
        if not results:
            yield "No knowledge found. Please upload documents first."
            return

        # Combine top chunks as context
        context = "\n\n".join(results[:3])

        # Generate answer from Ollama
        answer = generate_answer(context, question)

        # Stream word by word
        for word in answer.split():
            yield word + " "
            await asyncio.sleep(0.015)

    return StreamingResponse(event_stream(), media_type="text/plain")
