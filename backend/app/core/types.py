"""Database types that behave consistently across supported SQLAlchemy dialects."""

import uuid

from sqlalchemy import String
from sqlalchemy.types import TypeDecorator


class GUID(TypeDecorator):
    """Store UUID values as canonical 36-character strings.

    SQLite has no native UUID column type.  Converting at the database boundary
    preserves UUID values and lets application code continue to use ``uuid.UUID``.
    """

    impl = String(36)
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        if not isinstance(value, uuid.UUID):
            value = uuid.UUID(str(value))
        return str(value)

    def process_result_value(self, value, dialect):
        return uuid.UUID(value) if value is not None else None
