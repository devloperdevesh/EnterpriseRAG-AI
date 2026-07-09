from starlette.middleware.base import BaseHTTPMiddleware
from app.observability.logging import logger
import time

class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        logger.info(f"➡️ Incoming: {request.method} {request.url}")

        start = time.time()
        response = await call_next(request)
        duration = time.time() - start

        logger.info(f"⬅️ Completed: {response.status_code} in {duration:.3f}s")

        return response