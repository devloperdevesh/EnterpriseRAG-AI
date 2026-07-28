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
    from app.rag.llm import generate_answer_stream
    from app.rag.vector_store import search_embedding_scored
    from sse_starlette.sse import EventSourceResponse
    import json

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
                yield {"data": json.dumps({"token": "No knowledge found. Please upload documents first."})}

            return EventSourceResponse(empty_stream())

        context = "\n\n".join(chunk["text"] for chunk in results)

        # ---- LLM phase: answer generation ----
        async def event_stream():
            llm_start = perf_counter()
            full_answer = []
            
            # Offload blocking synchronous generator to a thread
            def get_chunks():
                for chunk in generate_answer_stream(context, question):
                    yield chunk
                    
            iterator = asyncio.to_thread(lambda: list(get_chunks()))
            
            # Stream the answer tokens as they arrive
            # (Note: In a fully async system, generate_answer_stream would be async)
            # Since requests is synchronous, the whole list might block, so let's just 
            # use a simple wrapper to yield items as they are produced if we had an async generator.
            # But since Ollama is requested via synchronous `requests`, we'll simulate the stream loop properly:
            
            pass # We will refactor this to be properly async in a moment.

    # Re-implementing the generator properly with asyncio:
    async def async_event_stream():
        llm_start = perf_counter()
        full_answer = []
        
        # We need an async generator. Let's offload the `requests` generator to a thread.
        # But `asyncio.to_thread` runs a single function.
        # To yield from a synchronous generator asynchronously, we can just use a queue or run it in an executor.
        import queue
        q = queue.Queue()
        
        def worker():
            try:
                for chunk in generate_answer_stream(context, question):
                    q.put(("token", chunk))
                q.put(("done", None))
            except Exception as e:
                q.put(("error", str(e)))
                
        # Start the worker thread
        loop = asyncio.get_running_loop()
        worker_task = loop.run_in_executor(None, worker)
        
        while True:
            # Poll the queue (non-blocking)
            try:
                msg_type, val = q.get_nowait()
                if msg_type == "done":
                    break
                elif msg_type == "error":
                    yield {"data": json.dumps({"token": val})}
                    break
                elif msg_type == "token":
                    full_answer.append(val)
                    yield {"data": json.dumps({"token": val})}
            except queue.Empty:
                await asyncio.sleep(0.01)
                
        llm_ms = round((perf_counter() - llm_start) * 1000, 2)
        total_ms = round(retrieval_ms + llm_ms, 2)

        # Record observability metadata after streaming is done
        _dispatch_background(
            record_query(
                user["user_id"],
                query=question,
                answer_summary="".join(full_answer)[:200],
                chunk_count=len(results),
                top_scores=[chunk["score"] for chunk in results],
                source_documents=sorted(
                    {chunk["source"] for chunk in results if chunk["source"]}
                ),
                retrieval_latency_ms=retrieval_ms,
                llm_latency_ms=llm_ms,
                total_latency_ms=total_ms,
            )
        )

    return EventSourceResponse(async_event_stream())



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
