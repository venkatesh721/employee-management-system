from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel


class EmployeeCreate(BaseModel):
    user_id: str | None = None
    department_id: str | None = None
    first_name: str
    last_name: str
    email: str
    phone: str | None = None
    position: str | None = None
    salary: Decimal | None = None
    date_of_birth: date | None = None
    date_of_hire: date | None = None
    address: str | None = None
    city: str | None = None
    state: str | None = None
    zip_code: str | None = None
    status: str = "active"


class EmployeeUpdate(BaseModel):
    user_id: str | None = None
    department_id: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    email: str | None = None
    phone: str | None = None
    position: str | None = None
    salary: Decimal | None = None
    date_of_birth: date | None = None
    date_of_hire: date | None = None
    address: str | None = None
    city: str | None = None
    state: str | None = None
    zip_code: str | None = None
    status: str | None = None


class EmployeeResponse(BaseModel):
    id: str
    employee_id: str
    user_id: str | None
    department_id: str | None
    first_name: str
    last_name: str
    email: str
    phone: str | None
    position: str | None
    salary: Decimal | None
    date_of_birth: date | None
    date_of_hire: date | None
    address: str | None
    city: str | None
    state: str | None
    zip_code: str | None
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class EmployeeListResponse(BaseModel):
    items: list[EmployeeResponse]
    total: int
    page: int
    size: int
    pages: int
