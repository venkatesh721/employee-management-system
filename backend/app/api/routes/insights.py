from datetime import date, timedelta

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import require_admin
from app.models.attendance import Attendance
from app.models.employee import Employee
from app.models.user import User
from app.services.audit import record_audit
from app.services.workforce_insights import generate_insights

router = APIRouter(prefix="/api/insights", tags=["Workforce Insights"])


class InsightRequest(BaseModel):
    focus: str = Field(default="", max_length=300)


@router.post("/workforce")
def workforce_insights(
    payload: InsightRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    start_date = date.today() - timedelta(days=29)
    attendance_records = (
        db.query(Attendance).filter(Attendance.date >= start_date).count()
    )
    present_records = (
        db.query(Attendance)
        .filter(Attendance.date >= start_date, Attendance.status == "present")
        .count()
    )
    metrics = {
        "period_days": 30,
        "total_employees": db.query(Employee).count(),
        "inactive_employees": db.query(Employee)
        .filter(Employee.status != "active")
        .count(),
        "attendance_records": attendance_records,
        "present_records": present_records,
    }
    generated, source = generate_insights(metrics, payload.focus.strip())
    record_audit(
        db, current_user, "generate", "workforce_insights", details={"source": source}
    )
    db.commit()
    return {"insights": generated, "source": source, "metrics": metrics}
