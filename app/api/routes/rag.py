from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import asyncio

from app.core.dependencies import get_current_user
from app.rag.embeddings import generate_embedding
from app.rag.vector_store import search_embedding
from app.rag.llm import generate_answer
from opentelemetry import trace

tracer = trace.get_tracer(__name__)

@router.post("/query")
async def query():

    with tracer.start_as_current_span("rag-query"):

        with tracer.start_as_current_span("vector-search"):
            pass

        with tracer.start_as_current_span("llm-call"):
            pass

        return {"ok": True}

router = APIRouter(prefix="/rag", tags=["rag"])


class RAGQuery(BaseModel):
    question: str


class ChunkPreviewRequest(BaseModel):
    text: str
    chunk_size: int = 500
    overlap: int = 50


class ChunkInfo(BaseModel):
    index: int
    text: str
    start_word: int
    end_word: int
    word_count: int
    overlap_prev: int
    overlap_next: int


class ChunkPreviewResponse(BaseModel):
    chunks: list[ChunkInfo]
    total_chunks: int
    total_words: int


@router.post("/chunk-preview", response_model=ChunkPreviewResponse)
def chunk_preview(data: ChunkPreviewRequest):
    from app.rag.chunker import chunk_text_with_overlap

    chunks = chunk_text_with_overlap(data.text, data.chunk_size, data.overlap)
    total_words = sum(c["word_count"] for c in chunks)

    return ChunkPreviewResponse(
        chunks=[ChunkInfo(**c) for c in chunks],
        total_chunks=len(chunks),
        total_words=total_words,
    )


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
