"""سرویس ثبت رویدادهای حسابرسی."""

from __future__ import annotations

import json

from sqlalchemy.orm import Session

from barekat_cell_therapy.core.config import get_settings
from barekat_cell_therapy.models.user import AuditLog


def write_audit(
    db: Session,
    action: str,
    resource_type: str,
    resource_id: str | None = None,
    actor_id: str | None = None,
    detail: dict | None = None,
) -> None:
    settings = get_settings()
    if not settings.audit_log_enabled:
        return
    row = AuditLog(
        actor_id=actor_id,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        detail_json=json.dumps(detail or {}, ensure_ascii=False),
    )
    db.add(row)
    db.commit()
