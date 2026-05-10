from fastapi import APIRouter
from fastapi.responses import StreamingResponse
import asyncio

router = APIRouter()

async def event_generator():

    for i in range(10):
        yield f"data: token-{i}\n\n"
        await asyncio.sleep(1)

@router.get("/stream")
async def stream():
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream"
    )