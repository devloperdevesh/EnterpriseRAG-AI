## Summary
This PR resolves a significant UX bottleneck in the `/rag/query/stream` endpoint by implementing true auto-regressive Server-Sent Events (SSE). 

Previously, the endpoint awaited the complete text generation from the LLM before yielding chunks for cosmetic UI streaming. By integrating `sse-starlette` and converting the Ollama client into a real-time generator, tokens are now streamed immediately as they arrive over an `EventSourceResponse`, drastically reducing perceived latency.

## Architectural Changes
- **Dependencies**: Added `sse-starlette` to manage the EventSource streaming protocol standard.
- **LLM Service (`app/rag/llm.py`)**: Implemented `generate_answer_stream` using `requests.post(stream=True)` to yield JSON-decoded tokens asynchronously.
- **FastAPI Routes (`app/api/routes/rag.py`)**: Offloaded the blocking generator to a background thread (`asyncio.to_thread`) and wrapped the output in an `EventSourceResponse`. Background metadata tracking via `_dispatch_background` remains intact.

*Note: Submitted as part of GirlScript Summer of Code (GSSoC) 2026.*
