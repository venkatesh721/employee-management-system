from datetime import date, timedelta

from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user, require_admin
from app.models.attendance import Attendance
from app.models.department import Department
from app.models.employee import Employee
from app.models.user import User
from app.models.payroll import PayrollRecord

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])


@router.get("/employee")
def employee_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    employee = db.query(Employee).filter(Employee.user_id == current_user.id).first()
    if not employee:
        return {
            "employee": None,
            "attendance_this_month": 0,
            "present_this_month": 0,
            "message": "No employee profile is linked to this account.",
        }
    start = date.today().replace(day=1)
    attendance = db.query(Attendance).filter(
        Attendance.employee_id == employee.id, Attendance.date >= start
    )
    payroll = (
        db.query(PayrollRecord)
        .filter(PayrollRecord.employee_id == employee.id)
        .order_by(PayrollRecord.payroll_month.desc())
        .limit(6)
        .all()
    )
    recent_attendance = attendance.order_by(Attendance.date.desc()).limit(7).all()
    return {
        "employee": {
            "employee_id": employee.employee_id,
            "name": f"{employee.first_name} {employee.last_name}",
            "position": employee.position,
            "status": employee.status,
        },
        "attendance_this_month": attendance.count(),
        "present_this_month": attendance.filter(Attendance.status == "present").count(),
        "late_this_month": attendance.filter(Attendance.status == "late").count(),
        "absent_this_month": attendance.filter(Attendance.status == "absent").count(),
        "latest_salary": (
            {
                "net_salary": payroll[0].net_salary,
                "gross_salary": payroll[0].gross_salary,
                "status": payroll[0].status,
                "month": payroll[0].payroll_month,
            }
            if payroll
            else None
        ),
        "salary_history": [
            {
                "id": str(row.id),
                "month": row.payroll_month,
                "gross_salary": row.gross_salary,
                "net_salary": row.net_salary,
                "status": row.status,
            }
            for row in reversed(payroll)
        ],
        "recent_attendance": [
            {
                "id": str(row.id),
                "date": row.date,
                "status": row.status,
                "check_in": row.check_in,
                "check_out": row.check_out,
            }
            for row in recent_attendance
        ],
        "message": "Welcome to your employee workspace.",
    }


@router.get("/stats")
def dashboard_stats(
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    total_employees = db.query(Employee).count()
    active_employees = db.query(Employee).filter(Employee.status == "active").count()
    total_departments = db.query(Department).count()
    today_attendance = (
        db.query(Attendance).filter(Attendance.date == date.today()).count()
    )

    return {
        "total_employees": total_employees,
        "active_employees": active_employees,
        "total_departments": total_departments,
        "today_attendance": today_attendance,
    }


@router.get("/attendance-chart")
def attendance_chart(
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    today = date.today()
    start = today - timedelta(days=29)
    rows = (
        db.query(
            Attendance.date,
            Attendance.status,
            func.count(Attendance.id).label("count"),
        )
        .filter(Attendance.date >= start, Attendance.date <= today)
        .group_by(Attendance.date, Attendance.status)
        .order_by(Attendance.date)
        .all()
    )

    data = {}
    for row in rows:
        day = row.date.isoformat()
        if day not in data:
            data[day] = {
                "date": day,
                "present": 0,
                "absent": 0,
                "late": 0,
                "half_day": 0,
            }
        status_key = row.status.replace("-", "_")
        data[day][status_key] = row.count

    return {"labels": list(data.keys()), "datasets": list(data.values())}


@router.get("/department-distribution")
def department_distribution(
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    results = (
        db.query(
            Department.name,
            func.count(Employee.id).label("count"),
        )
        .join(Employee, Employee.department_id == Department.id, isouter=True)
        .group_by(Department.name)
        .order_by(Department.name)
        .all()
    )

    return [{"department": r.name, "count": r.count} for r in results]


@router.get("/recent-employees")
def recent_employees(
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    employees = db.query(Employee).order_by(Employee.created_at.desc()).limit(5).all()

    return [
        {
            "id": str(emp.id),
            "employee_id": emp.employee_id,
            "full_name": f"{emp.first_name} {emp.last_name}",
            "email": emp.email,
            "position": emp.position,
            "status": emp.status,
            "created_at": emp.created_at.isoformat() if emp.created_at else None,
        }
        for emp in employees
    ]
