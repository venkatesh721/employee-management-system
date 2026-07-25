from datetime import datetime

from pydantic import BaseModel

from app.schemas.employee import EmployeeResponse


class DepartmentCreate(BaseModel):
    name: str
    description: str | None = None
    manager_id: str | None = None


class DepartmentUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    manager_id: str | None = None


class DepartmentResponse(BaseModel):
    id: str
    name: str
    description: str | None
    manager_id: str | None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class DepartmentWithEmployeeCount(BaseModel):
    id: str
    name: str
    description: str | None
    manager_id: str | None
    employee_count: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class DepartmentDetailResponse(DepartmentResponse):
    employees: list[EmployeeResponse] = []

    class Config:
        from_attributes = True
