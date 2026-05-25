from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import generate_latest
from starlette.responses import Response

from app.api.routes.auth import router as auth_router
from app.api.routes.dashboard import router as dashboard_router
from app.api.routes.document import router as document_router
from app.api.routes.rag import router as rag_router
from app.api.routes.tenants import router as tenants_router
from app.core.config import settings
from app.core.dependencies import get_current_user
from app.db.init_db import init_db
from app.middleware.middleware import MetricsMiddleware
from app.middleware.middleware_logging import LoggingMiddleware

try:
    from app.observability.tracing import setup_tracing
except ImportError:  # pragma: no cover - tracing is optional in local/test envs
    def setup_tracing():
        return None

app = FastAPI(title=settings.APP_NAME)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "https://enterpriserag-ai.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(LoggingMiddleware)
app.add_middleware(MetricsMiddleware)

app.include_router(auth_router)
app.include_router(dashboard_router)
app.include_router(tenants_router)
app.include_router(document_router)
app.include_router(rag_router)

setup_tracing()


@app.on_event("startup")
def startup_event():
    init_db()


@app.get("/")
def root():
    return {"message": "EnterpriseRAG backend running"}


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type="text/plain")


@app.get("/protected")
def protected(user=Depends(get_current_user)):
    return {
        "message": "You are authenticated",
        "user": user,
    }


@app.get("/admin/metrics")
def protected_metrics(user=Depends(get_current_user)):
    if user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not allowed",
        )

    return Response(generate_latest(), media_type="text/plain")
