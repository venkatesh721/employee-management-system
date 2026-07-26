import uuid
from datetime import datetime, timezone
from sqlalchemy import (
    Column,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.core.types import GUID


class LeaveRequest(Base):
    __tablename__ = "leave_requests"
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    employee_id = Column(
        GUID(),
        ForeignKey("employees.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    leave_type = Column(String(30), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    reason = Column(Text, nullable=False)
    status = Column(String(20), nullable=False, default="pending", index=True)
    admin_remarks = Column(Text)
    reviewed_by = Column(GUID(), ForeignKey("users.id", ondelete="SET NULL"))
    reviewed_at = Column(DateTime(timezone=True))
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    employee = relationship("Employee", back_populates="leave_requests")


class LeaveBalance(Base):
    __tablename__ = "leave_balances"
    __table_args__ = (
        UniqueConstraint("employee_id", "leave_type", name="uq_leave_balance_type"),
    )
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    employee_id = Column(
        GUID(), ForeignKey("employees.id", ondelete="CASCADE"), nullable=False
    )
    leave_type = Column(String(30), nullable=False)
    allocated_days = Column(Integer, nullable=False, default=20)
    used_days = Column(Integer, nullable=False, default=0)
