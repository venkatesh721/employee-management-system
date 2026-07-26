import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from app.core.database import Base
from app.core.types import GUID


class PolicyDocument(Base):
    __tablename__ = "policy_documents"
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    uploaded_by = Column(GUID(), ForeignKey("users.id", ondelete="SET NULL"))
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )


class PolicyDocumentChunk(Base):
    __tablename__ = "policy_document_chunks"
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    document_id = Column(
        GUID(),
        ForeignKey("policy_documents.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    chunk_index = Column(Integer, nullable=False)
    section = Column(String(255))
    content = Column(Text, nullable=False)
