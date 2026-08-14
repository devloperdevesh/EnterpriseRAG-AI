from fastapi import APIRouter, HTTPException, status

router = APIRouter(
    prefix="/health",
    tags=["health"],
)

is_ready = False


@router.get("/live")
def liveness():
    return {"status": "alive"}


@router.get("/ready")
def readiness():
    if not is_ready:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service not ready",
        )

    return {"status": "ready"}