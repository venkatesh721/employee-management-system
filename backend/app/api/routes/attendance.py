import math
import uuid
from datetime import date, datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.attendance import Attendance
from app.models.employee import Employee
from app.models.user import User
from app.schemas.attendance import (
    AttendanceCreate,
    AttendanceListResponse,
    AttendanceResponse,
    AttendanceUpdate,
)

router = APIRouter(prefix="/api/attendance", tags=["Attendance"])


def _attendance_to_response(rec: Attendance) -> AttendanceResponse:
    return AttendanceResponse(
        id=str(rec.id),
        employee_id=str(rec.employee_id),
        date=rec.date,
        check_in=rec.check_in,
        check_out=rec.check_out,
        status=rec.status,
        notes=rec.notes,
    )


@router.get("", response_model=AttendanceListResponse)
def list_attendance(
    employee_id: str | None = Query(None),
    date_from: date | None = Query(None),
    date_to: date | None = Query(None),
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    query = db.query(Attendance)

    if employee_id:
        query = query.filter(Attendance.employee_id == uuid.UUID(employee_id))
    if date_from:
        query = query.filter(Attendance.date >= date_from)
    if date_to:
        query = query.filter(Attendance.date <= date_to)

    total = query.count()
    pages = max(1, math.ceil(total / size))
    records = query.order_by(Attendance.date.desc(), Attendance.check_in.desc()).offset(
        (page - 1) * size
    ).limit(size).all()

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
    _: User = Depends(get_current_user),
):
    emp = db.query(Employee).filter(Employee.id == uuid.UUID(payload.employee_id)).first()
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")

    existing = db.query(Attendance).filter(
        Attendance.employee_id == uuid.UUID(payload.employee_id),
        Attendance.date == payload.date,
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Already checked in for this date")

    record = Attendance(
        id=uuid.uuid4(),
        employee_id=uuid.UUID(payload.employee_id),
        date=payload.date,
        check_in=payload.check_in,
        status=payload.status,
        notes=payload.notes,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return _attendance_to_response(record)


@router.put("/{attendance_id}", response_model=AttendanceResponse)
def update_attendance(
    attendance_id: str,
    payload: AttendanceUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    record = db.query(Attendance).filter(Attendance.id == uuid.UUID(attendance_id)).first()
    if not record:
        raise HTTPException(status_code=404, detail="Attendance record not found")

    update_data = payload.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(record, key, value)
    if not record.check_out:
        record.status = "present"

    db.commit()
    db.refresh(record)
    return _attendance_to_response(record)


@router.get("/today", response_model=list[AttendanceResponse])
def get_today_attendance(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    today = date.today()
    records = db.query(Attendance).filter(Attendance.date == today).all()
    return [_attendance_to_response(r) for r in records]


@router.get("/summary")
def attendance_summary(
    period: str = Query("monthly", regex="^(daily|weekly|monthly)$"),
    employee_id: str | None = Query(None),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
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

    if employee_id:
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
    }
