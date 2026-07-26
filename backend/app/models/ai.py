import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, DateTime, ForeignKey, Numeric, String, Text
from app.core.database import Base
from app.core.types import GUID


class AIInsight(Base):
    __tablename__ = "ai_insights"
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    employee_id = Column(
        GUID(), ForeignKey("employees.id", ondelete="CASCADE"), index=True
    )
    insight_type = Column(String(50), nullable=False)
    risk_level = Column(String(20))
    score = Column(Numeric(5, 2))
    explanation = Column(Text, nullable=False)
    model_version = Column(String(50), nullable=False, default="rules-v1")
    generated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )


class AIAnomaly(Base):
    __tablename__ = "ai_anomalies"
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    employee_id = Column(
        GUID(), ForeignKey("employees.id", ondelete="CASCADE"), index=True
    )
    resource_type = Column(String(30), nullable=False)
    resource_id = Column(String(100))
    score = Column(Numeric(7, 3))
    expected_range = Column(String(100))
    actual_value = Column(String(100))
    explanation = Column(Text, nullable=False)
    model_version = Column(String(50), nullable=False, default="threshold-v1")
    generated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
