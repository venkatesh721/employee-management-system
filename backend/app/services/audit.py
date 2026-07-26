import json

from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog
from app.models.user import User


def record_audit(
    db: Session,
    user: User,
    action: str,
    resource_type: str,
    resource_id=None,
    details: dict | None = None,
) -> None:
    db.add(
        AuditLog(
            user_id=user.id,
            action=action,
            resource_type=resource_type,
            resource_id=str(resource_id) if resource_id else None,
            details=json.dumps(details, default=str) if details else None,
        )
    )
