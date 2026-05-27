from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import Response
from prometheus_client import generate_latest

from app.core.config import settings
from app.core.dependencies import get_current_user

from app.api.routes.auth import router as auth_router
from app.api.routes.tenants import router as tenants_router
from app.api.routes.document import router as document_router
from app.api.routes.rag import router as rag_router

from app.middleware.middleware import MetricsMiddleware
from app.middleware.middleware_logging import LoggingMiddleware
from app.reliability.rate_limit import init_redis
from app.db.init_db import init_db
from app.observability.tracing import setup_tracing

# ===============================
# Create FastAPI App
# ===============================
app = FastAPI(title=settings.APP_NAME)

# ===============================
# Tracing
# ===============================
setup_tracing()

# ===============================
# Middlewares
# ===============================
app.add_middleware(LoggingMiddleware)
app.add_middleware(MetricsMiddleware)
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

# ===============================
# Startup Event
# ===============================
@app.on_event("startup")
async def startup_event():
    init_db()
    await init_redis()

# ===============================
# Metrics Endpoint
# ===============================
@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type="text/plain")

# ===============================
# Routers
# ===============================
app.include_router(auth_router)
app.include_router(tenants_router)
app.include_router(document_router)
app.include_router(rag_router)

# ===============================
# Health & Basic Routes
# ===============================
@app.get("/")
def root():
    return {"message": "EnterpriseRAG backend running"}

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.get("/protected")
def protected(user=Depends(get_current_user)):
    return {
        "message": "You are authenticated",
        "user": user,
    }