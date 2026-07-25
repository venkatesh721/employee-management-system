from datetime import date, datetime

from pydantic import BaseModel


class AttendanceCreate(BaseModel):
    employee_id: str
    date: date
    check_in: datetime
    status: str = "present"
    notes: str | None = None


class AttendanceUpdate(BaseModel):
    check_out: datetime | None = None
    status: str | None = None
    notes: str | None = None


class AttendanceResponse(BaseModel):
    id: str
    employee_id: str
    date: date
    check_in: datetime
    check_out: datetime | None
    status: str
    notes: str | None

    class Config:
        from_attributes = True


class AttendanceListResponse(BaseModel):
    items: list[AttendanceResponse]
    total: int
    page: int
    size: int
    pages: int
