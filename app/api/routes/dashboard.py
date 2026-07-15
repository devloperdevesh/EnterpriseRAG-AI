from fastapi import APIRouter, Depends

from app.core.dependencies import get_current_user

router = APIRouter(
    prefix="/dashboard",
    tags=["dashboard"],
)


@router.get("/session")
def dashboard_session(current_user=Depends(get_current_user)):
    return {
        "message": "Dashboard access granted",
        "user": current_user,
    }
