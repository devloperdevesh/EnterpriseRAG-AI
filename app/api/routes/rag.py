from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from opentelemetry.propagate import inject
from app.workers.celery_worker import process_document
import asyncio

from opentelemetry import trace

from app.core.dependencies import get_current_user

from app.rag.embeddings import generate_embedding
from app.rag.vector_store import search_embedding
from app.rag.llm import generate_answer

router = APIRouter(
    prefix="/rag",
    tags=["rag"]
)

tracer = trace.get_tracer(__name__)


class RAGQuery(BaseModel):
    question: str


# ===============================
# Basic Traced Query
# ===============================

@router.post("/query")
async def query():

    with tracer.start_as_current_span("rag-query"):

        with tracer.start_as_current_span("vector-search"):
            pass

        with tracer.start_as_current_span("llm-call"):
            pass

        trace_headers = {}

        inject(trace_headers)

        process_document.apply_async(
            args=["sample-doc-id"],
            headers=trace_headers
        )

        return {"ok": True}


# ===============================
# Streaming Query
# ===============================

@router.post("/query/stream")
async def stream_query(
    data: RAGQuery,
    user=Depends(get_current_user)
):

    question = data.question

    with tracer.start_as_current_span("rag-stream-query"):

        # Create embedding
        with tracer.start_as_current_span("generate-embedding"):
            query_emb = generate_embedding(question)

        # Search vector DB
        with tracer.start_as_current_span("vector-search"):
            results = search_embedding(query_emb)

        async def event_stream():

            with tracer.start_as_current_span("sse-stream"):

                # No docs
                if not results:
                    yield "No knowledge found. Please upload documents first."
                    return

                # Use top chunk
                context = results[0]

                # Generate answer
                with tracer.start_as_current_span("llm-generation"):
                    answer = generate_answer(
                        context,
                        question
                    )

                # Stream tokens
                for word in answer.split():

                    with tracer.start_as_current_span(
                        "stream-token"
                    ) as span:

                        span.set_attribute(
                            "token.value",
                            word
                        )

                        yield word + " "

                        await asyncio.sleep(0.015)

        return StreamingResponse(
            event_stream(),
            media_type="text/plain"
        )