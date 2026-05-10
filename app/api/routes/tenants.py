from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.db.deps import get_db
from app.models.tenant import Tenant

router = APIRouter(prefix="/tenants", tags=["tenants"])

@router.get("/me")
def get_my_tenant(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    tenant = db.query(Tenant).filter(
        Tenant.id == current_user["tenant_id"]
    ).first()

    return tenant