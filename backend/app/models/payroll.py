import uuid
from datetime import datetime, timezone
from sqlalchemy import (
    Column,
    Date,
    DateTime,
    ForeignKey,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.core.types import GUID


class SalaryStructure(Base):
    __tablename__ = "salary_structures"
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    employee_id = Column(
        GUID(),
        ForeignKey("employees.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )
    basic_salary = Column(Numeric(12, 2), nullable=False, default=0)
    hra = Column(Numeric(12, 2), nullable=False, default=0)
    allowances = Column(Numeric(12, 2), nullable=False, default=0)
    tax = Column(Numeric(12, 2), nullable=False, default=0)
    provident_fund = Column(Numeric(12, 2), nullable=False, default=0)
    insurance = Column(Numeric(12, 2), nullable=False, default=0)
    other_deductions = Column(Numeric(12, 2), nullable=False, default=0)
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
    employee = relationship("Employee", back_populates="salary_structure")


class PayrollRecord(Base):
    __tablename__ = "payroll_records"
    __table_args__ = (
        UniqueConstraint(
            "employee_id", "payroll_month", name="uq_payroll_employee_month"
        ),
    )
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    employee_id = Column(
        GUID(),
        ForeignKey("employees.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    payroll_month = Column(Date, nullable=False, index=True)
    basic_salary = Column(Numeric(12, 2), nullable=False, default=0)
    hra = Column(Numeric(12, 2), nullable=False, default=0)
    allowances = Column(Numeric(12, 2), nullable=False, default=0)
    bonus = Column(Numeric(12, 2), nullable=False, default=0)
    overtime = Column(Numeric(12, 2), nullable=False, default=0)
    tax = Column(Numeric(12, 2), nullable=False, default=0)
    provident_fund = Column(Numeric(12, 2), nullable=False, default=0)
    insurance = Column(Numeric(12, 2), nullable=False, default=0)
    other_deductions = Column(Numeric(12, 2), nullable=False, default=0)
    gross_salary = Column(Numeric(12, 2), nullable=False)
    total_deductions = Column(Numeric(12, 2), nullable=False)
    net_salary = Column(Numeric(12, 2), nullable=False)
    status = Column(String(20), nullable=False, default="draft")
    payment_date = Column(Date, nullable=True)
    payment_reference = Column(String(100), nullable=True)
    created_by = Column(GUID(), ForeignKey("users.id", ondelete="SET NULL"))
    updated_by = Column(GUID(), ForeignKey("users.id", ondelete="SET NULL"))
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
    employee = relationship("Employee", back_populates="payroll_records")


class PayrollAuditLog(Base):
    __tablename__ = "payroll_audit_logs"
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    payroll_id = Column(
        GUID(),
        ForeignKey("payroll_records.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user_id = Column(GUID(), ForeignKey("users.id", ondelete="SET NULL"))
    action = Column(String(50), nullable=False)
    reason = Column(Text, nullable=True)
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
