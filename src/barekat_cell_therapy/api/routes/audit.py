"""Audit log endpoints."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from barekat_cell_therapy.core.database import get_db
from barekat_cell_therapy.core.rbac import require_role
from barekat_cell_therapy.models.user import AuditLog, User
from barekat_cell_therapy.schemas import AuditLogResponse

router = APIRouter()


@router.get("/audit/", response_model=list[AuditLogResponse])
def list_audit(
    limit: int = 50,
    db: Session = Depends(get_db),
    _: User | None = Depends(require_role("scientist")),
) -> list[AuditLogResponse]:
    rows = db.query(AuditLog).order_by(AuditLog.id.desc()).limit(min(limit, 200)).all()
    return [
        AuditLogResponse(
            id=r.id,
            actor_id=r.actor_id,
            action=r.action,
            resource_type=r.resource_type,
            resource_id=r.resource_id,
            detail_json=r.detail_json,
            created_at=r.created_at,
        )
        for r in rows
    ]
