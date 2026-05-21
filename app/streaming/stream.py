from fastapi import APIRouter
from fastapi.responses import StreamingResponse

import asyncio

from opentelemetry import trace

router = APIRouter()

tracer = trace.get_tracer(__name__)


async def event_generator():

    with tracer.start_as_current_span(
        "sse-event-generator"
    ):

        for i in range(10):

            with tracer.start_as_current_span(
                "sse-token"
            ) as span:

                span.set_attribute(
                    "token.index",
                    i
                )

                yield f"data: token-{i}\n\n"

                await asyncio.sleep(1)


@router.get("/stream")
async def stream():

    with tracer.start_as_current_span(
        "sse-stream-request"
    ):

        return StreamingResponse(
            event_generator(),
            media_type="text/event-stream"
        )