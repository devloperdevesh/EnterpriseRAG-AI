from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware

from core.config import settings
from core.dependencies import get_current_user
from db.init_db import init_db

from api.routes.auth import router as auth_router
# from api.v1.tenants import router as tenants_router
# from api.v1.document import router as document_router
# from api.v1.rag import router as rag_router
from fastapi import FastAPI
# from prometheus_client import generate_latest
from starlette.responses import Response
# from middleware.middleware import MetricsMiddleware
# from middleware.middleware_logging import LoggingMiddleware
# from reliability.rate_limit import init_redis
from fastapi import Depends, HTTPException
from core.dependencies import get_current_user

app = FastAPI(title=settings.APP_NAME)

# @app.get("/metrics")
# def metrics(user=Depends(get_current_user)):
#     if user.get("sub") != "admin":
#         raise HTTPException(status_code=403, detail="Not allowed")

#     return Response(generate_latest(), media_type="text/plain")



# @app.on_event("startup")
# async def startup():
#     await init_redis()


# app.add_middleware(LoggingMiddleware)



# app.add_middleware(MetricsMiddleware)

# @app.get("/metrics")
# def metrics():
#     return Response(generate_latest(), media_type="text/plain")




# ===============================
# Create FastAPI App
# ===============================


# ===============================
# Initialize DB
# ===============================
@app.on_event("startup")
def startup_event():
    init_db()

# ===============================
# CORS (FINAL & CORRECT)
# ===============================
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
# Routers
# ===============================
app.include_router(auth_router)
# app.include_router(tenants_router)
# app.include_router(document_router)
# app.include_router(rag_router)

# ===============================
# Health Routes
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
        "message": "You are authenticated, YESS!",
        "user": user,
    }


# from observability.tracing import setup_tracing

# setup_tracing()