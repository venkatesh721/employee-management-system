import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import require_admin
from app.models.department import Department
from app.models.employee import Employee
from app.models.user import User
from app.schemas.department import (
    DepartmentCreate,
    DepartmentDetailResponse,
    DepartmentResponse,
    DepartmentUpdate,
    DepartmentWithEmployeeCount,
)
from app.schemas.employee import EmployeeResponse

router = APIRouter(prefix="/api/departments", tags=["Departments"])


def _dept_to_response(dept: Department) -> DepartmentResponse:
    return DepartmentResponse(
        id=str(dept.id),
        name=dept.name,
        description=dept.description,
        manager_id=str(dept.manager_id) if dept.manager_id else None,
        created_at=dept.created_at,
        updated_at=dept.updated_at,
    )


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


@router.get("", response_model=list[DepartmentWithEmployeeCount])
def list_departments(
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    departments = (
        db.query(Department)
        .order_by(Department.created_at.asc(), Department.id.asc())
        .all()
    )
    result = []
    for dept in departments:
        count = db.query(Employee).filter(Employee.department_id == dept.id).count()
        result.append(
            DepartmentWithEmployeeCount(
                id=str(dept.id),
                name=dept.name,
                description=dept.description,
                manager_id=str(dept.manager_id) if dept.manager_id else None,
                employee_count=count,
                created_at=dept.created_at,
                updated_at=dept.updated_at,
            )
        )
    return result


@router.post("", response_model=DepartmentResponse, status_code=status.HTTP_201_CREATED)
def create_department(
    payload: DepartmentCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    if db.query(Department).filter(Department.name == payload.name).first():
        raise HTTPException(status_code=400, detail="Department name already exists")

    dept = Department(
        id=uuid.uuid4(),
        name=payload.name,
        description=payload.description,
        manager_id=uuid.UUID(payload.manager_id) if payload.manager_id else None,
    )
    db.add(dept)
    db.commit()
    db.refresh(dept)
    return _dept_to_response(dept)


@router.get("/{department_id}", response_model=DepartmentDetailResponse)
def get_department(
    department_id: str,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    dept = (
        db.query(Department).filter(Department.id == uuid.UUID(department_id)).first()
    )
    if not dept:
        raise HTTPException(status_code=404, detail="Department not found")

    employees = db.query(Employee).filter(Employee.department_id == dept.id).all()
    return DepartmentDetailResponse(
        id=str(dept.id),
        name=dept.name,
        description=dept.description,
        manager_id=str(dept.manager_id) if dept.manager_id else None,
        created_at=dept.created_at,
        updated_at=dept.updated_at,
        employees=[_employee_to_response(e) for e in employees],
    )


@router.put("/{department_id}", response_model=DepartmentResponse)
def update_department(
    department_id: str,
    payload: DepartmentUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    dept = (
        db.query(Department).filter(Department.id == uuid.UUID(department_id)).first()
    )
    if not dept:
        raise HTTPException(status_code=404, detail="Department not found")

    update_data = payload.model_dump(exclude_unset=True)
    if "manager_id" in update_data and update_data["manager_id"]:
        update_data["manager_id"] = uuid.UUID(update_data["manager_id"])

    for key, value in update_data.items():
        setattr(dept, key, value)

    db.commit()
    db.refresh(dept)
    return _dept_to_response(dept)


@router.delete("/{department_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_department(
    department_id: str,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    dept = (
        db.query(Department).filter(Department.id == uuid.UUID(department_id)).first()
    )
    if not dept:
        raise HTTPException(status_code=404, detail="Department not found")

    emp_count = db.query(Employee).filter(Employee.department_id == dept.id).count()
    if emp_count > 0:
        raise HTTPException(
            status_code=400,
            detail="Cannot delete department with existing employees",
        )

    db.delete(dept)
    db.commit()
