import math
import uuid
from datetime import date, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user, require_admin
from app.models.attendance import Attendance
from app.models.employee import Employee
from app.models.user import User
from app.services.audit import record_audit
from sqlalchemy.exc import IntegrityError
from app.schemas.attendance import (
    AttendanceCreate,
    AttendanceListResponse,
    AttendanceResponse,
    AttendanceUpdate,
)

router = APIRouter(prefix="/api/attendance", tags=["Attendance"])


def _own_employee(db: Session, user: User) -> Employee:
    employee = db.query(Employee).filter(Employee.user_id == user.id).first()
    if not employee:
        raise HTTPException(
            status_code=404,
            detail="No employee profile is linked to this account. Contact an administrator.",
        )
    return employee


def _attendance_to_response(rec: Attendance) -> AttendanceResponse:
    hours = 0.0
    if rec.check_in and rec.check_out:
        hours = round((rec.check_out - rec.check_in).total_seconds() / 3600, 2)
    return AttendanceResponse(
        id=str(rec.id),
        employee_id=str(rec.employee_id),
        employee_name=f"{rec.employee.first_name} {rec.employee.last_name}".strip()
        if rec.employee
        else None,
        date=rec.date,
        check_in=rec.check_in,
        check_out=rec.check_out,
        status=rec.status,
        notes=rec.notes,
        working_hours=hours,
        created_at=rec.created_at,
        updated_at=rec.updated_at,
    )


@router.get("", response_model=AttendanceListResponse)
def list_attendance(
    employee_id: str | None = Query(None),
    date_from: date | None = Query(None),
    date_to: date | None = Query(None),
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(Attendance)
    if current_user.role != "admin" and not current_user.is_superuser:
        query = query.filter(
            Attendance.employee_id == _own_employee(db, current_user).id
        )

    if employee_id and (current_user.role == "admin" or current_user.is_superuser):
        query = query.filter(Attendance.employee_id == uuid.UUID(employee_id))
    if date_from:
        query = query.filter(Attendance.date >= date_from)
    if date_to:
        query = query.filter(Attendance.date <= date_to)

    total = query.count()
    pages = max(1, math.ceil(total / size))
    records = (
        query.order_by(Attendance.date.desc(), Attendance.check_in.desc())
        .offset((page - 1) * size)
        .limit(size)
        .all()
    )

    return AttendanceListResponse(
        items=[_attendance_to_response(r) for r in records],
        total=total,
        page=page,
        size=size,
        pages=pages,
    )


@router.post("", response_model=AttendanceResponse, status_code=status.HTTP_201_CREATED)
def check_in(
    payload: AttendanceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    emp = (
        db.query(Employee).filter(Employee.id == uuid.UUID(payload.employee_id)).first()
    )
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")

    existing = (
        db.query(Attendance)
        .filter(
            Attendance.employee_id == emp.id,
            Attendance.date == payload.date,
        )
        .first()
    )
    if existing:
        raise HTTPException(
            status_code=409,
            detail="Attendance already exists for this employee and date",
        )

    record = Attendance(
        id=uuid.uuid4(),
        employee_id=emp.id,
        date=payload.date,
        check_in=payload.check_in,
        check_out=payload.check_out,
        status=payload.status,
        notes=payload.notes,
        created_by=current_user.id,
        updated_by=current_user.id,
    )
    db.add(record)
    record_audit(
        db,
        current_user,
        "create",
        "attendance",
        record.id,
        {"employee_id": str(emp.id), "date": str(payload.date)},
    )
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Attendance already exists for this employee and date",
        )
    db.refresh(record)
    return _attendance_to_response(record)


@router.put("/{attendance_id}", response_model=AttendanceResponse)
def update_attendance(
    attendance_id: str,
    payload: AttendanceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    record = (
        db.query(Attendance).filter(Attendance.id == uuid.UUID(attendance_id)).first()
    )
    if not record:
        raise HTTPException(status_code=404, detail="Attendance record not found")
    update_data = payload.model_dump(exclude_unset=True)
    audit_reason = update_data.pop("audit_reason")
    for key, value in update_data.items():
        setattr(record, key, value)
    record.updated_by = current_user.id
    record_audit(
        db,
        current_user,
        "update",
        "attendance",
        record.id,
        {
            "reason": audit_reason,
            "changes": {k: str(v) for k, v in update_data.items()},
        },
    )

    db.commit()
    db.refresh(record)
    return _attendance_to_response(record)


@router.get("/today", response_model=AttendanceResponse | None)
def get_today_attendance(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    today = date.today()
    query = db.query(Attendance).filter(Attendance.date == today)
    if current_user.role != "admin" and not current_user.is_superuser:
        query = query.filter(
            Attendance.employee_id == _own_employee(db, current_user).id
        )
    record = query.order_by(Attendance.check_in.desc()).first()
    return _attendance_to_response(record) if record else None


@router.get("/summary")
def attendance_summary(
    period: str = Query("monthly", regex="^(daily|weekly|monthly)$"),
    employee_id: str | None = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    today = date.today()
    if period == "daily":
        start_date = today
    elif period == "weekly":
        start_date = today - timedelta(days=today.weekday())
    else:
        start_date = today.replace(day=1)

    query = db.query(
        Attendance.status,
        func.count(Attendance.id).label("count"),
    ).filter(Attendance.date >= start_date)
    if current_user.role != "admin" and not current_user.is_superuser:
        query = query.filter(
            Attendance.employee_id == _own_employee(db, current_user).id
        )

    if employee_id and (current_user.role == "admin" or current_user.is_superuser):
        query = query.filter(Attendance.employee_id == uuid.UUID(employee_id))

    results = query.group_by(Attendance.status).all()

    total = sum(r.count for r in results)
    breakdown = {r.status: r.count for r in results}

    return {
        "period": period,
        "start_date": start_date.isoformat(),
        "end_date": today.isoformat(),
        "total_records": total,
        "breakdown": breakdown,
        **{"present": 0, "absent": 0, "late": 0, "half_day": 0, "leave": 0},
        **breakdown,
    }
