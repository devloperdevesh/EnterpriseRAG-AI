import asyncio
from contextlib import nullcontext
from time import perf_counter

from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

try:
    from opentelemetry import trace
except ImportError:  # pragma: no cover - observability is optional in tests
    class _NoopTracer:
        def start_as_current_span(self, *_args, **_kwargs):
            return nullcontext()

    class _NoopTrace:
        @staticmethod
        def get_tracer(_name):
            return _NoopTracer()

    trace = _NoopTrace()

from app.core.dependencies import get_current_user
from app.observability.metrics_log import record_metric
from app.rag.query_history import record_query, get_history, MAX_HISTORY_PER_USER

router = APIRouter(prefix="/rag", tags=["rag"])
tracer = trace.get_tracer(__name__)

router = APIRouter(prefix="/rag", tags=["rag"])

# Words/sec pacing for the smooth token stream (purely cosmetic; excluded from
# the latency measurements stored in query history).
STREAM_WORD_DELAY = 0.015

# Strong references to in-flight fire-and-forget tasks so the event loop does
# not garbage-collect them before they finish.
_background_tasks: set[asyncio.Task] = set()


def _dispatch_background(coro) -> None:
    """Schedule a coroutine fire-and-forget, without blocking the response."""
    task = asyncio.create_task(coro)
    _background_tasks.add(task)
    task.add_done_callback(_background_tasks.discard)


class RAGQuery(BaseModel):
    question: str = Field(..., max_length=500)


@router.post("/query/stream")
async def stream_query(data: RAGQuery, user=Depends(get_current_user)):
    """Answer a question over the indexed documents and stream the response.

    Latency is measured around two phases -- retrieval (embedding + vector
    search) and LLM generation -- and, together with retrieval metadata, is
    persisted to the per-user Redis query history for later inspection.
    """
    question = data.question
    from app.rag.embeddings import generate_embedding
    from app.rag.llm import generate_answer_with_usage
    from app.rag.vector_store import search_embedding_scored

    with tracer.start_as_current_span("rag-query"):
        # ---- Retrieval phase: embedding + vector search ----
        retrieval_start = perf_counter()
        with tracer.start_as_current_span("vector-search"):
            query_emb = await asyncio.to_thread(generate_embedding, question)
            results = await asyncio.to_thread(search_embedding_scored, query_emb, 3)
        retrieval_ms = round((perf_counter() - retrieval_start) * 1000, 2)

        # No indexed documents -> stream a hint, nothing to record.
        if not results:
            async def empty_stream():
                yield "No knowledge found. Please upload documents first."

            return StreamingResponse(empty_stream(), media_type="text/plain")

        context = "\n\n".join(chunk["text"] for chunk in results)

        # ---- LLM phase: answer generation ----
        llm_start = perf_counter()
        with tracer.start_as_current_span("llm-call"):
            answer, usage = await asyncio.to_thread(
                generate_answer_with_usage, context, question
            )
        llm_ms = round((perf_counter() - llm_start) * 1000, 2)
        total_ms = round(retrieval_ms + llm_ms, 2)

        top_scores = [chunk["score"] for chunk in results]
        source_documents = sorted(
            {chunk["source"] for chunk in results if chunk["source"]}
        )

        # ---- Record observability metadata ----
        # Dispatched fire-and-forget (with an internal timeout) so a slow Redis
        # can never delay the user-visible response stream.
        _dispatch_background(
            record_query(
                user["user_id"],
                query=question,
                answer_summary=answer[:200],
                chunk_count=len(results),
                top_scores=top_scores,
                source_documents=source_documents,
                retrieval_latency_ms=retrieval_ms,
                llm_latency_ms=llm_ms,
                total_latency_ms=total_ms,
            )
        )

        # ---- Record tenant-wide dashboard metrics (issue #117) ----
        _dispatch_background(
            record_metric(
                user.get("tenant_id"),
                user_id=user["user_id"],
                query=question,
                prompt_tokens=usage["prompt_tokens"],
                completion_tokens=usage["completion_tokens"],
                total_tokens=usage["total_tokens"],
                retrieval_latency_ms=retrieval_ms,
                llm_latency_ms=llm_ms,
                total_latency_ms=total_ms,
                top_score=max(top_scores) if top_scores else 0.0,
                chunk_count=len(results),
                source_documents=source_documents,
            )
        )

    async def event_stream():
        # Stream the (already-generated) answer word by word for a smooth UI.
        for word in answer.split():
            yield word + " "
            await asyncio.sleep(STREAM_WORD_DELAY)

    return StreamingResponse(event_stream(), media_type="text/plain")


@router.get("/history")
async def query_history(
    limit: int = Query(MAX_HISTORY_PER_USER, ge=1, le=MAX_HISTORY_PER_USER),
    user=Depends(get_current_user),
):
    """Return the most recent RAG queries for the current user.

    Backed by short-lived Redis storage (1h TTL); see
    :mod:`app.rag.query_history`.
    """
    items = await get_history(user["user_id"], limit=limit)
    return {
        "scope": f"user:{user['user_id']}",
        "count": len(items),
        "items": items,
    }
