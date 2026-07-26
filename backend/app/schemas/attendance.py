from __future__ import annotations

from datetime import date as Date, datetime

from pydantic import BaseModel
from typing import Literal


class AttendanceCreate(BaseModel):
    employee_id: str
    date: Date
    check_in: datetime | None = None
    check_out: datetime | None = None
    status: Literal["present", "absent", "late", "half_day", "on_leave"] = "present"
    notes: str | None = None


class AttendanceUpdate(BaseModel):
    check_in: datetime | None = None
    check_out: datetime | None = None
    status: Literal["present", "absent", "late", "half_day", "on_leave"] | None = None
    notes: str | None = None
    audit_reason: str


class AttendanceResponse(BaseModel):
    id: str
    employee_id: str
    date: Date
    employee_name: str | None = None
    check_in: datetime | None
    check_out: datetime | None
    working_hours: float
    status: str
    notes: str | None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AttendanceListResponse(BaseModel):
    items: list[AttendanceResponse]
    total: int
    page: int
    size: int
    pages: int
