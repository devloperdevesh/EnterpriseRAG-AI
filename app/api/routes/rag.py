import asyncio

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from opentelemetry import trace
from pydantic import BaseModel

from app.core.dependencies import get_current_user
from app.rag.embeddings import generate_embedding
from app.rag.llm import generate_answer
from app.rag.vector_store import search_embedding


router = APIRouter(prefix="/rag", tags=["rag"])
tracer = trace.get_tracer(__name__)


class RAGQuery(BaseModel):
    query: str


@router.post("/query")
async def query(data: RAGQuery, user=Depends(get_current_user)):
    question = data.query

    with tracer.start_as_current_span("rag-query"):
        with tracer.start_as_current_span("vector-search"):
            query_embedding = generate_embedding(question)
            results = search_embedding(query_embedding)

        if not results:
            return {"answer": "No knowledge found. Please upload documents first."}

        with tracer.start_as_current_span("llm-call"):
            answer = generate_answer(results[0], question)

    return {"answer": answer}


@router.post("/query/stream")
async def stream_query(data: RAGQuery, user=Depends(get_current_user)):
    question = data.query
    query_embedding = generate_embedding(question)
    results = search_embedding(query_embedding)

    async def event_stream():
        if not results:
            yield "No knowledge found. Please upload documents first."
            return

        answer = generate_answer(results[0], question)
        for word in answer.split():
            yield word + " "
            await asyncio.sleep(0.015)

    return StreamingResponse(event_stream(), media_type="text/plain")
