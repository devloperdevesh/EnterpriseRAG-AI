from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import asyncio

from app.core.dependencies import get_current_user
from app.rag.embeddings import generate_embedding
from app.rag.vector_store import search_embedding
from app.rag.llm import generate_answer

router = APIRouter(prefix="/rag", tags=["rag"])


class RAGQuery(BaseModel):
    question: str


@router.post("/query/stream")
async def stream_query(data: RAGQuery, user=Depends(get_current_user)):
    question = data.question

    # Create embedding for question
    query_emb = generate_embedding(question)

    # Search vector DB
    results = search_embedding(query_emb)

    async def event_stream():
        # No docs case
        if not results:
            yield "No knowledge found. Please upload documents first."
            return

        # Use top relevant chunk
        context = results[0]

        # Ask Ollama
        answer = generate_answer(context, question)

        # Stream answer smoothly
        for word in answer.split():
            yield word + " "
            await asyncio.sleep(0.015)

    return StreamingResponse(event_stream(), media_type="text/plain")
