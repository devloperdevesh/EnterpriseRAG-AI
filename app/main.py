import logging

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.dependencies import get_current_user

from app.api.v1.auth import router as auth_router
from app.api.v1.tenants import router as tenants_router
from app.api.v1.document import router as document_router
from app.api.v1.rag import router as rag_router
from prometheus_client import generate_latest
from starlette.responses import Response
from app.core.middleware import MetricsMiddleware
from app.core.middleware_logging import LoggingMiddleware
from app.core.rate_limit import init_redis
from app.db import init_db
from fastapi import HTTPException

logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.APP_NAME,
    docs_url="/docs",
    redoc_url="/redoc",
)

# ---------------------------
# CORS Middleware
# ---------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(MetricsMiddleware)
app.add_middleware(LoggingMiddleware)

# ---------------------------
# Routers
# ---------------------------
app.include_router(auth_router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(tenants_router, prefix="/api/v1/tenants", tags=["tenants"])
app.include_router(document_router, prefix="/api/v1/documents", tags=["documents"])
app.include_router(rag_router, prefix="/api/v1/rag", tags=["rag"])


# ---------------------------
# Startup Event
# ---------------------------
@app.on_event("startup")
async def startup_event() -> None:
    """
    Application startup handler.

    Initialises the database and Redis connection pool.
    Raises RuntimeError to abort startup if either resource is unavailable,
    ensuring the application never starts in a broken state.
    """
    try:
        init_db()
        logger.info("Database initialised successfully.")
    except Exception as exc:
        logger.critical("Database initialisation failed: %s", exc, exc_info=True)
        raise RuntimeError(
            f"Startup aborted — database unavailable: {exc}"
        ) from exc

    try:
        await init_redis()
        logger.info("Redis connection pool ready.")
    except Exception as exc:
        logger.warning("Redis initialisation failed: %s", exc, exc_info=True)
        # Redis failure is non-fatal (degraded mode); log and continue.


# ---------------------------
# Metrics Endpoint
# ---------------------------
@app.get("/metrics", include_in_schema=False)
def metrics(user=Depends(get_current_user)):
    """Prometheus metrics endpoint — admin only."""
    if user.get("sub") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return Response(generate_latest(), media_type="text/plain")
