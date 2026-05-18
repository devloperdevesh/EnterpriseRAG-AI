from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import generate_latest
from starlette.responses import Response

from app.core.config import settings
from app.core.dependencies import get_current_user
from app.db.init_db import init_db

# Corrected Imports
from app.middleware.middleware import MetricsMiddleware
from app.middleware.middleware_logging import LoggingMiddleware
from app.reliability.rate_limit import init_redis
from app.observability.tracing import setup_tracing

from app.api.routes.auth import router as auth_router
from app.api.routes.tenants import router as tenants_router
from app.api.routes.document import router as document_router
from app.api.routes.rag import router as rag_router

# Initialize Tracing
setup_tracing()

# Single Instance Definition
app = FastAPI(title=settings.APP_NAME)

# Middlewares
app.add_middleware(LoggingMiddleware)
app.add_middleware(MetricsMiddleware)

# CORS
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

# Startup Hook
@app.on_event("startup")
async def startup_event():
    await init_redis()
    init_db()

# Routers
app.include_router(auth_router)
app.include_router(tenants_router)
app.include_router(document_router)
app.include_router(rag_router)

# Health & Metrics Routes
@app.get("/metrics")
def metrics(user=Depends(get_current_user)):
    if user.get("sub") != "admin":
        raise HTTPException(status_code=403, detail="Not allowed")
    return Response(generate_latest(), media_type="text/plain")

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