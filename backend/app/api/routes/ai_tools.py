import re
from datetime import date, timedelta
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import func
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user, require_admin
from app.models.attendance import Attendance
from app.models.employee import Employee
from app.models.payroll import PayrollRecord
from app.models.user import User

router = APIRouter(prefix="/api/ai", tags=["AI decision support"])
MODEL = "transparent-rules-v1"


class Question(BaseModel):
    question: str


def risk_for(db, employee):
    start = date.today() - timedelta(days=30)
    rows = (
        db.query(Attendance)
        .filter(Attendance.employee_id == employee.id, Attendance.date >= start)
        .all()
    )
    counts = {
        s: sum(r.status == s for r in rows) for s in ("absent", "late", "half_day")
    }
    score = min(
        100, counts["absent"] * 20 + counts["late"] * 10 + counts["half_day"] * 8
    )
    level = "high" if score >= 60 else "medium" if score >= 30 else "low"
    factors = [
        f"{v} {k.replace('_', ' ')} record(s) in the last 30 days"
        for k, v in counts.items()
        if v
    ]
    return {
        "employee_id": str(employee.id),
        "employee_name": f"{employee.first_name} {employee.last_name}",
        "risk_level": level,
        "score": score,
        "confidence": 0.8 if rows else 0.4,
        "factors": factors or ["Insufficient adverse attendance signals"],
        "explanation": "Decision-support only; human review is required.",
        "model_version": MODEL,
    }


@router.get("/attendance-risk")
def attendance_risk(
    db: Session = Depends(get_db), user: User = Depends(get_current_user)
):
    if user.role == "admin" or user.is_superuser:
        employees = db.query(Employee).all()
    else:
        employee = db.query(Employee).filter(Employee.user_id == user.id).first()
        if not employee:
            raise HTTPException(
                404,
                "No employee profile is linked to this account. Contact an administrator.",
            )
        employees = [employee]
    return [risk_for(db, e) for e in employees]


@router.get("/anomalies")
def anomalies(db: Session = Depends(get_db), _: User = Depends(require_admin)):
    alerts = []
    for employee in db.query(Employee).all():
        risk = risk_for(db, employee)
        if risk["risk_level"] != "low":
            alerts.append(
                {
                    "type": "attendance",
                    "employee_id": str(employee.id),
                    "actual_value": risk["score"],
                    "expected_range": "0-29",
                    "explanation": ", ".join(risk["factors"]),
                    "model_version": MODEL,
                }
            )
        payroll = (
            db.query(PayrollRecord)
            .filter(PayrollRecord.employee_id == employee.id)
            .order_by(PayrollRecord.payroll_month.desc())
            .limit(2)
            .all()
        )
        if (
            len(payroll) == 2
            and payroll[1].net_salary
            and abs(payroll[0].net_salary - payroll[1].net_salary)
            / payroll[1].net_salary
            > 0.25
        ):
            alerts.append(
                {
                    "type": "payroll",
                    "employee_id": str(employee.id),
                    "actual_value": str(payroll[0].net_salary),
                    "expected_range": "within 25% of previous month",
                    "explanation": "Net salary changed by more than 25%; human review required.",
                    "model_version": MODEL,
                }
            )
    return alerts


@router.post("/hr-assistant")
def assistant(
    payload: Question, db: Session = Depends(get_db), _: User = Depends(require_admin)
):
    q = payload.question.lower()
    start = date.today().replace(day=1)
    if "total payroll" in q:
        value = (
            db.query(func.coalesce(func.sum(PayrollRecord.net_salary), 0))
            .filter(PayrollRecord.payroll_month == start)
            .scalar()
        )
        return {
            "query_type": "monthly_payroll_total",
            "result": {"total": str(value)},
            "explanation": "Sum of current-month net payroll using an allow-listed aggregate.",
            "model_version": MODEL,
        }
    if "late" in q:
        rows = (
            db.query(Employee.first_name, Employee.last_name, func.count(Attendance.id))
            .join(Attendance)
            .filter(Attendance.date >= start, Attendance.status == "late")
            .group_by(Employee.id)
            .all()
        )
        return {
            "query_type": "late_arrivals",
            "result": [{"employee": f"{a} {b}", "count": c} for a, b, c in rows],
            "explanation": "Current-month late records from an allow-listed query.",
            "model_version": MODEL,
        }
    match = re.search(r"absent more than (\\d+)", q)
    if match:
        n = int(match.group(1))
        rows = (
            db.query(
                Employee.first_name,
                Employee.last_name,
                func.count(Attendance.id).label("count"),
            )
            .join(Attendance)
            .filter(Attendance.date >= start, Attendance.status == "absent")
            .group_by(Employee.id)
            .having(func.count(Attendance.id) > n)
            .all()
        )
        return {
            "query_type": "absence_threshold",
            "result": [{"employee": f"{a} {b}", "count": c} for a, b, c in rows],
            "explanation": "Allow-listed attendance threshold query.",
            "model_version": MODEL,
        }
    raise HTTPException(
        422,
        "Supported questions cover total payroll, repeated late arrivals, and absence thresholds.",
    )
