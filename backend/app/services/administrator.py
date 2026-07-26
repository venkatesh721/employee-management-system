import logging

from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import hash_password
from app.models.user import User

logger = logging.getLogger(__name__)


def ensure_default_administrator(db: Session) -> bool:
    """Create the single default administrator, safely and idempotently."""
    existing = (
        db.query(User)
        .filter(or_(User.role == "admin", User.is_superuser.is_(True)))
        .first()
    )
    if existing:
        return False

    administrator = User(
        email=settings.DEFAULT_ADMIN_EMAIL.lower(),
        username=settings.DEFAULT_ADMIN_USERNAME,
        hashed_password=hash_password(settings.DEFAULT_ADMIN_PASSWORD),
        full_name=settings.DEFAULT_ADMIN_NAME,
        role="admin",
        is_superuser=True,
        is_active=True,
    )
    db.add(administrator)
    try:
        db.commit()
    except IntegrityError:
        # Multiple application instances can start together. The database
        # constraint selects one winner and prevents a duplicate administrator.
        db.rollback()
        existing = (
            db.query(User)
            .filter(or_(User.role == "admin", User.is_superuser.is_(True)))
            .first()
        )
        if existing:
            return False
        raise
    logger.info("Created the default administrator account")
    return True
