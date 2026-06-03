import time
from starlette.middleware.base import BaseHTTPMiddleware
from app.observability.metrics import REQUEST_COUNT, REQUEST_LATENCY

class MetricsMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        start_time = time.time()
        
        response = await call_next(request)
        
        process_time = time.time() - start_time
        
        REQUEST_COUNT.labels(
            request.method,
            request.url.path,
            response.status_code
        ).inc()
        
        REQUEST_LATENCY.labels(
            request.url.path
        ).observe(process_time)
        
        return response