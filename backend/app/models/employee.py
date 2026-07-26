import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, Date, DateTime, ForeignKey, Numeric, String, Text
from sqlalchemy.orm import relationship

from app.core.database import Base
from app.core.types import GUID


class Employee(Base):
    __tablename__ = "employees"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    employee_id = Column(String(20), unique=True, nullable=False, index=True)
    user_id = Column(
        GUID(),
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
        unique=True,
        index=True,
    )
    department_id = Column(
        GUID(), ForeignKey("departments.id", ondelete="SET NULL"), nullable=True
    )
    first_name = Column(String(150), nullable=False)
    last_name = Column(String(150), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    phone = Column(String(20), nullable=True)
    position = Column(String(255), nullable=True)
    salary = Column(Numeric(12, 2), nullable=True)
    date_of_birth = Column(Date, nullable=True)
    date_of_hire = Column(Date, nullable=True)
    address = Column(Text, nullable=True)
    city = Column(String(100), nullable=True)
    state = Column(String(100), nullable=True)
    zip_code = Column(String(20), nullable=True)
    status = Column(String(20), default="active", nullable=False)
    created_at = Column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    user = relationship("User")
    department = relationship(
        "Department", foreign_keys=[department_id], back_populates="employees"
    )
    attendance_records = relationship("Attendance", back_populates="employee")
    salary_structure = relationship(
        "SalaryStructure", back_populates="employee", uselist=False
    )
    payroll_records = relationship("PayrollRecord", back_populates="employee")
    leave_requests = relationship("LeaveRequest", back_populates="employee")
