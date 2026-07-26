import math
import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user, hash_password, require_admin
from app.models.employee import Employee
from app.models.user import User
from app.schemas.employee import (
    EmployeeCreate,
    EmployeeListResponse,
    EmployeeResponse,
    EmployeeUpdate,
)
from app.services.audit import record_audit

router = APIRouter(prefix="/api/employees", tags=["Employees"])


def _generate_employee_id(db: Session) -> str:
    last = db.query(Employee).order_by(Employee.created_at.desc()).first()
    if last and last.employee_id.startswith("EMP"):
        num = int(last.employee_id[3:]) + 1
    else:
        num = 1
    return f"EMP{num:03d}"


def _employee_to_response(emp: Employee) -> EmployeeResponse:
    account = emp.user
    return EmployeeResponse(
        id=str(emp.id),
        employee_id=emp.employee_id,
        user_id=str(emp.user_id) if emp.user_id else None,
        department_id=str(emp.department_id) if emp.department_id else None,
        first_name=emp.first_name,
        last_name=emp.last_name,
        email=emp.email,
        role=account.role if account else None,
        is_active=account.is_active if account else None,
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
    _: User = Depends(require_admin),
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
    current_user: User = Depends(require_admin),
):
    if payload.role != "employee":
        raise HTTPException(
            status_code=400,
            detail="Additional administrator accounts cannot be created",
        )
    if db.query(Employee).filter(Employee.email == payload.email).first():
        raise HTTPException(status_code=400, detail="Email already in use")

    if db.query(User).filter(User.email == str(payload.email).lower()).first():
        raise HTTPException(
            status_code=400, detail="A login account already uses this email"
        )

    username_base = str(payload.email).split("@")[0].replace(".", "_")[:120]
    username = username_base
    suffix = 1
    while db.query(User).filter(User.username == username).first():
        suffix += 1
        username = f"{username_base}_{suffix}"

    account = User(
        id=uuid.uuid4(),
        email=str(payload.email).lower(),
        username=username,
        hashed_password=hash_password(payload.password),
        full_name=f"{payload.first_name} {payload.last_name}".strip(),
        role=payload.role,
        is_active=payload.status == "active",
        is_superuser=payload.role == "admin",
    )
    db.add(account)
    db.flush()

    employee = Employee(
        id=uuid.uuid4(),
        employee_id=_generate_employee_id(db),
        user_id=account.id,
        department_id=uuid.UUID(payload.department_id)
        if payload.department_id
        else None,
        first_name=payload.first_name,
        last_name=payload.last_name,
        email=str(payload.email).lower(),
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
    db.flush()
    record_audit(
        db,
        current_user,
        "create",
        "employee",
        employee.id,
        {"employee_id": employee.employee_id, "role": payload.role},
    )
    db.commit()
    db.refresh(employee)
    return _employee_to_response(employee)


@router.get("/me", response_model=EmployeeResponse)
def get_own_employee(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    emp = db.query(Employee).filter(Employee.user_id == current_user.id).first()
    if not emp:
        raise HTTPException(
            status_code=404, detail="No employee profile is linked to this account"
        )
    return _employee_to_response(emp)


@router.get("/warnings/unlinked-accounts")
def unlinked_accounts(db: Session = Depends(get_db), _: User = Depends(require_admin)):
    rows = (
        db.query(User)
        .outerjoin(Employee, Employee.user_id == User.id)
        .filter(User.role == "employee", Employee.id.is_(None))
        .all()
    )
    return [
        {
            "user_id": str(u.id),
            "email": u.email,
            "username": u.username,
            "warning": "Employee account has no linked profile",
        }
        for u in rows
    ]


@router.get("/{employee_id}", response_model=EmployeeResponse)
def get_employee(
    employee_id: str,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
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
    current_user: User = Depends(require_admin),
):
    emp = db.query(Employee).filter(Employee.id == uuid.UUID(employee_id)).first()
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")

    update_data = payload.model_dump(exclude_unset=True)
    new_password = update_data.pop("password", None)
    new_role = update_data.pop("role", None)
    if new_role and new_role != "employee":
        raise HTTPException(
            status_code=400,
            detail="Employee accounts cannot be promoted to administrator",
        )
    new_active = update_data.pop("is_active", None)
    if "user_id" in update_data and update_data["user_id"]:
        update_data["user_id"] = uuid.UUID(update_data["user_id"])
    if "department_id" in update_data and update_data["department_id"]:
        update_data["department_id"] = uuid.UUID(update_data["department_id"])
    if "email" in update_data:
        existing = (
            db.query(Employee)
            .filter(Employee.email == update_data["email"], Employee.id != emp.id)
            .first()
        )
        if existing:
            raise HTTPException(status_code=400, detail="Email already in use")

    for key, value in update_data.items():
        setattr(emp, key, value)

    if emp.user:
        emp.user.email = emp.email
        emp.user.full_name = f"{emp.first_name} {emp.last_name}".strip()
        if new_password:
            emp.user.hashed_password = hash_password(new_password)
        if new_role:
            emp.user.role = new_role
            emp.user.is_superuser = new_role == "admin"
        if new_active is not None:
            emp.user.is_active = new_active
        elif "status" in update_data:
            emp.user.is_active = emp.status == "active"
    record_audit(db, current_user, "update", "employee", emp.id, update_data)
    db.commit()
    db.refresh(emp)
    return _employee_to_response(emp)


@router.delete("/{employee_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_employee(
    employee_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    emp = db.query(Employee).filter(Employee.id == uuid.UUID(employee_id)).first()
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")
    emp.status = "terminated"
    if emp.user:
        emp.user.is_active = False
    record_audit(db, current_user, "deactivate", "employee", emp.id)
    db.commit()
