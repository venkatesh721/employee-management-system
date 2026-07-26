import uuid
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, model_validator
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user, require_admin
from app.models.attendance import Attendance
from app.models.employee import Employee
from app.models.leave import LeaveBalance, LeaveRequest
from app.models.user import User
from app.services.audit import record_audit

router = APIRouter(prefix="/api/leaves", tags=["Leave"])


class LeaveInput(BaseModel):
    leave_type: str
    start_date: datetime | None = None
    end_date: datetime | None = None
    reason: str

    @model_validator(mode="after")
    def valid_dates(self):
        if (
            not self.start_date
            or not self.end_date
            or self.end_date.date() < self.start_date.date()
        ):
            raise ValueError("End date must be on or after start date")
        return self


class ReviewInput(BaseModel):
    status: str
    remarks: str | None = None


def own_employee(db, user):
    row = db.query(Employee).filter(Employee.user_id == user.id).first()
    if not row:
        raise HTTPException(
            404,
            "No employee profile is linked to this account. Contact an administrator.",
        )
    return row


def serialize(row):
    return {c.name: getattr(row, c.name) for c in row.__table__.columns}


@router.post("", status_code=status.HTTP_201_CREATED)
def apply_leave(
    payload: LeaveInput,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    if user.role == "admin" or user.is_superuser:
        raise HTTPException(403, "Administrators cannot submit employee leave requests")
    employee = own_employee(db, user)
    start, end = payload.start_date.date(), payload.end_date.date()
    overlap = (
        db.query(LeaveRequest)
        .filter(
            LeaveRequest.employee_id == employee.id,
            LeaveRequest.status.in_(["pending", "approved"]),
            LeaveRequest.start_date <= end,
            LeaveRequest.end_date >= start,
        )
        .first()
    )
    if overlap:
        raise HTTPException(409, "Leave request overlaps an existing request")
    days = (end - start).days + 1
    balance = (
        db.query(LeaveBalance)
        .filter(
            LeaveBalance.employee_id == employee.id,
            LeaveBalance.leave_type == payload.leave_type,
        )
        .first()
    )
    if not balance:
        balance = LeaveBalance(
            employee_id=employee.id,
            leave_type=payload.leave_type,
            allocated_days=20,
            used_days=0,
        )
        db.add(balance)
    if balance.allocated_days - balance.used_days < days:
        raise HTTPException(422, "Insufficient leave balance")
    row = LeaveRequest(
        employee_id=employee.id,
        leave_type=payload.leave_type,
        start_date=start,
        end_date=end,
        reason=payload.reason,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return serialize(row)


@router.get("")
def list_leaves(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    query = db.query(LeaveRequest)
    if user.role != "admin" and not user.is_superuser:
        query = query.filter(LeaveRequest.employee_id == own_employee(db, user).id)
    return [serialize(r) for r in query.order_by(LeaveRequest.created_at.desc()).all()]


@router.get("/balances")
def balances(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    employee = own_employee(db, user)
    rows = db.query(LeaveBalance).filter(LeaveBalance.employee_id == employee.id).all()
    return [
        {**serialize(r), "available_days": r.allocated_days - r.used_days} for r in rows
    ]


@router.put("/{leave_id}/review")
def review(
    leave_id: str,
    payload: ReviewInput,
    db: Session = Depends(get_db),
    user: User = Depends(require_admin),
):
    if payload.status not in ("approved", "rejected"):
        raise HTTPException(422, "Status must be approved or rejected")
    row = db.query(LeaveRequest).filter(LeaveRequest.id == uuid.UUID(leave_id)).first()
    if not row:
        raise HTTPException(404, "Leave request not found")
    if row.status != "pending":
        raise HTTPException(409, "Leave request has already been reviewed")
    row.status, row.admin_remarks, row.reviewed_by, row.reviewed_at = (
        payload.status,
        payload.remarks,
        user.id,
        datetime.now(timezone.utc),
    )
    if payload.status == "approved":
        days = (row.end_date - row.start_date).days + 1
        balance = (
            db.query(LeaveBalance)
            .filter(
                LeaveBalance.employee_id == row.employee_id,
                LeaveBalance.leave_type == row.leave_type,
            )
            .first()
        )
        if not balance or balance.allocated_days - balance.used_days < days:
            raise HTTPException(422, "Insufficient leave balance")
        balance.used_days += days
        day = row.start_date
        while day <= row.end_date:
            attendance = (
                db.query(Attendance)
                .filter(
                    Attendance.employee_id == row.employee_id, Attendance.date == day
                )
                .first()
            )
            if attendance:
                attendance.status = "on_leave"
                attendance.updated_by = user.id
            else:
                db.add(
                    Attendance(
                        employee_id=row.employee_id,
                        date=day,
                        status="on_leave",
                        created_by=user.id,
                        updated_by=user.id,
                    )
                )
            day += timedelta(days=1)
    record_audit(
        db, user, payload.status, "leave_request", row.id, {"remarks": payload.remarks}
    )
    db.commit()
    db.refresh(row)
    return serialize(row)
