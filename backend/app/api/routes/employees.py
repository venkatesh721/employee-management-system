import math
import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.employee import Employee
from app.models.user import User
from app.schemas.employee import (
    EmployeeCreate,
    EmployeeListResponse,
    EmployeeResponse,
    EmployeeUpdate,
)

router = APIRouter(prefix="/api/employees", tags=["Employees"])


def _generate_employee_id(db: Session) -> str:
    last = db.query(Employee).order_by(Employee.created_at.desc()).first()
    if last and last.employee_id.startswith("EMP"):
        num = int(last.employee_id[3:]) + 1
    else:
        num = 1
    return f"EMP{num:03d}"


def _employee_to_response(emp: Employee) -> EmployeeResponse:
    return EmployeeResponse(
        id=str(emp.id),
        employee_id=emp.employee_id,
        user_id=str(emp.user_id) if emp.user_id else None,
        department_id=str(emp.department_id) if emp.department_id else None,
        first_name=emp.first_name,
        last_name=emp.last_name,
        email=emp.email,
        phone=emp.phone,
        position=emp.position,
        salary=emp.salary,
        date_of_birth=emp.date_of_birth,
        date_of_hire=emp.date_of_hire,
        address=emp.address,
        city=emp.city,
        state=emp.state,
        zip_code=emp.zip_code,
        status=emp.status,
        created_at=emp.created_at,
        updated_at=emp.updated_at,
    )


@router.get("", response_model=EmployeeListResponse)
def list_employees(
    search: str | None = Query(None),
    department_id: str | None = Query(None),
    status: str | None = Query(None),
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    sort_by: str = Query("created_at"),
    sort_order: str = Query("desc", regex="^(asc|desc)$"),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    query = db.query(Employee)

    if search:
        like = f"%{search}%"
        query = query.filter(
            or_(
                Employee.first_name.ilike(like),
                Employee.last_name.ilike(like),
                Employee.email.ilike(like),
                Employee.position.ilike(like),
                Employee.employee_id.ilike(like),
            )
        )
    if department_id:
        query = query.filter(Employee.department_id == uuid.UUID(department_id))
    if status:
        query = query.filter(Employee.status == status)

    total = query.count()
    pages = max(1, math.ceil(total / size))
    sort_col = getattr(Employee, sort_by, Employee.created_at)
    order_fn = sort_col.desc() if sort_order == "desc" else sort_col.asc()
    employees = query.order_by(order_fn).offset((page - 1) * size).limit(size).all()

    return EmployeeListResponse(
        items=[_employee_to_response(e) for e in employees],
        total=total,
        page=page,
        size=size,
        pages=pages,
    )


@router.post("", response_model=EmployeeResponse, status_code=status.HTTP_201_CREATED)
def create_employee(
    payload: EmployeeCreate,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    if db.query(Employee).filter(Employee.email == payload.email).first():
        raise HTTPException(status_code=400, detail="Email already in use")

    employee = Employee(
        id=uuid.uuid4(),
        employee_id=_generate_employee_id(db),
        user_id=uuid.UUID(payload.user_id) if payload.user_id else None,
        department_id=uuid.UUID(payload.department_id) if payload.department_id else None,
        first_name=payload.first_name,
        last_name=payload.last_name,
        email=payload.email,
        phone=payload.phone,
        position=payload.position,
        salary=payload.salary,
        date_of_birth=payload.date_of_birth,
        date_of_hire=payload.date_of_hire,
        address=payload.address,
        city=payload.city,
        state=payload.state,
        zip_code=payload.zip_code,
        status=payload.status,
    )
    db.add(employee)
    db.commit()
    db.refresh(employee)
    return _employee_to_response(employee)


@router.get("/{employee_id}", response_model=EmployeeResponse)
def get_employee(
    employee_id: str,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    emp = db.query(Employee).filter(Employee.id == uuid.UUID(employee_id)).first()
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")
    return _employee_to_response(emp)


@router.put("/{employee_id}", response_model=EmployeeResponse)
def update_employee(
    employee_id: str,
    payload: EmployeeUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    emp = db.query(Employee).filter(Employee.id == uuid.UUID(employee_id)).first()
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")

    update_data = payload.model_dump(exclude_unset=True)
    if "user_id" in update_data and update_data["user_id"]:
        update_data["user_id"] = uuid.UUID(update_data["user_id"])
    if "department_id" in update_data and update_data["department_id"]:
        update_data["department_id"] = uuid.UUID(update_data["department_id"])
    if "email" in update_data:
        existing = db.query(Employee).filter(
            Employee.email == update_data["email"], Employee.id != emp.id
        ).first()
        if existing:
            raise HTTPException(status_code=400, detail="Email already in use")

    for key, value in update_data.items():
        setattr(emp, key, value)

    db.commit()
    db.refresh(emp)
    return _employee_to_response(emp)


@router.delete("/{employee_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_employee(
    employee_id: str,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    emp = db.query(Employee).filter(Employee.id == uuid.UUID(employee_id)).first()
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")
    emp.status = "terminated"
    db.commit()
