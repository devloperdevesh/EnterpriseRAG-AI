# ===============================
# 1. ALL IMPORTS AT THE TOP (Fixes E402)
# ===============================
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import Response
from prometheus_client import generate_latest

from app.core.config import settings
from app.core.dependencies import get_current_user
from app.api.v1.auth import router as auth_router
from app.api.v1.tenants import router as tenants_router
from app.api.v1.document import router as document_router
from app.api.v1.rag import router as rag_router

from core.middleware import MetricsMiddleware
from core.middleware_logging import LoggingMiddleware
from core.rate_limit import init_redis
from core.tracing import setup_tracing
from app.db.init_db import init_db

# Initialize Tracing
setup_tracing()

# ===============================
# 2. CREATE FASTAPI APP
# ===============================
app = FastAPI(title=settings.APP_NAME)

# ===============================
# 3. ADD MIDDLEWARES
# ===============================
app.add_middleware(LoggingMiddleware)
app.add_middleware(MetricsMiddleware)

# CORS Middleware
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
# 4. STARTUP EVENTS (Merged & Correct)
# ===============================
@app.on_event("startup")
async def startup_event():
    init_db()          # Initialize Database
    await init_redis() # Initialize Redis Rate Limiter

# ===============================
# 5. ROUTERS
# ===============================
app.include_router(auth_router)
app.include_router(tenants_router)
app.include_router(document_router)
app.include_router(rag_router)

# ===============================
# 6. API ROUTES & HEALTH CHECKS
# ===============================
@app.get("/")
def root():
    return {"message": "EnterpriseRAG backend running"}

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.get("/metrics")
def metrics(user=Depends(get_current_user)):
    if user.get("sub") != "admin":
        raise HTTPException(status_code=403, detail="Not allowed")
    return Response(generate_latest(), media_type="text/plain")

@app.get("/protected")
def protected(user=Depends(get_current_user)):
    return {
        "message": "You are authenticated",
        "user": user,
    }
