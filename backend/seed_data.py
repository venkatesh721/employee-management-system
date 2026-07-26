"""Idempotent local demo seed data. Never use these passwords in production."""

import uuid
from datetime import date, datetime, time, timedelta, timezone
from decimal import Decimal

from sqlalchemy import or_

from app.core.database import Base, SessionLocal, engine
from app.core.config import settings
from app.core.security import hash_password
from app.models.attendance import Attendance
from app.models.department import Department
from app.models.employee import Employee
from app.models.user import User
from app.models.payroll import PayrollRecord, SalaryStructure
from app.models.leave import LeaveBalance, LeaveRequest

if settings.ENVIRONMENT.lower() == "production":
    raise RuntimeError("Demo seed data is disabled in production")

Base.metadata.create_all(bind=engine)

DEMO_USERS = [
    {
        "email": settings.DEFAULT_ADMIN_EMAIL or "admin@example.com",
        "username": settings.DEFAULT_ADMIN_USERNAME or "venkatesh",
        "password": settings.DEFAULT_ADMIN_PASSWORD or "Admin@123",
        "full_name": settings.DEFAULT_ADMIN_NAME or "Venkatesh",
        "role": "admin",
    },
    {
        "email": "employee1@globalco.example",
        "username": "globalco_employee1",
        "password": "EmployeeDemo123!",
        "full_name": "Aisha Kumar",
        "role": "employee",
        "employee_id": "EMP001",
        "position": "Software Engineer",
    },
    {
        "email": "employee2@globalco.example",
        "username": "globalco_employee2",
        "password": "EmployeeDemo123!",
        "full_name": "Daniel Lee",
        "role": "employee",
        "employee_id": "EMP002",
        "position": "QA Engineer",
    },
    {
        "email": "employee3@globalco.example",
        "username": "globalco_employee3",
        "password": "EmployeeDemo123!",
        "full_name": "Priya Sharma",
        "role": "employee",
        "employee_id": "EMP003",
        "position": "HR Specialist",
    },
    {
        "email": "employee4@globalco.example",
        "username": "globalco_employee4",
        "password": "EmployeeDemo123!",
        "full_name": "Marcus Johnson",
        "role": "employee",
        "employee_id": "EMP004",
        "position": "Product Manager",
    },
    {
        "email": "employee5@globalco.example",
        "username": "globalco_employee5",
        "password": "EmployeeDemo123!",
        "full_name": "Sofia Martinez",
        "role": "employee",
        "employee_id": "EMP005",
        "position": "UI/UX Designer",
    },
]


def seed():
    db = SessionLocal()
    try:
        department = (
            db.query(Department).filter(Department.name == "Engineering").first()
        )
        if not department:
            department = Department(
                id=uuid.uuid4(),
                name="Engineering",
                description="Product engineering and quality delivery",
            )
            db.add(department)
            db.flush()

        admin_user = None
        employee_rows = []
        for item in DEMO_USERS:
            user = (
                db.query(User)
                .filter(
                    or_(
                        User.email == item["email"],
                        User.username == item["username"],
                    )
                )
                .first()
            )
            if not user:
                user = User(
                    id=uuid.uuid4(),
                    email=item["email"],
                    username=item["username"],
                    hashed_password=hash_password(item["password"]),
                    full_name=item["full_name"],
                    role=item["role"],
                    is_active=True,
                    is_superuser=item["role"] == "admin",
                )
                db.add(user)
                db.flush()
            else:
                user.email = item["email"]
                user.hashed_password = hash_password(item["password"])
                user.full_name = item["full_name"]
                user.role = item["role"]
                user.is_superuser = item["role"] == "admin"
                user.is_active = True

            if item["role"] == "employee":
                employee = (
                    db.query(Employee).filter(Employee.user_id == user.id).first()
                )
                first_name, last_name = item["full_name"].split(" ", 1)
                if not employee:
                    employee_code = item["employee_id"]
                    sequence = 100
                    while (
                        db.query(Employee)
                        .filter(Employee.employee_id == employee_code)
                        .first()
                    ):
                        employee_code = f"EMP{sequence:03d}"
                        sequence += 1
                    employee = Employee(
                        id=uuid.uuid4(),
                        employee_id=employee_code,
                        user_id=user.id,
                        department_id=department.id,
                        first_name=first_name,
                        last_name=last_name,
                        email=item["email"],
                        position=item["position"],
                        date_of_hire=date.today(),
                        status="active",
                    )
                    db.add(employee)
                    db.flush()
                else:
                    employee.email = item["email"]
                    employee.first_name = first_name
                    employee.last_name = last_name
                    employee.position = item["position"]
                    employee.status = "active"
                employee_rows.append(employee)
            else:
                admin_user = user

        db.flush()
        employee_rows = (
            db.query(Employee)
            .join(User, Employee.user_id == User.id)
            .filter(User.role == "employee", User.is_active.is_(True))
            .all()
        )
        today = date.today()
        for employee_index, employee in enumerate(employee_rows):
            basic = Decimal("42000.00") + Decimal(employee_index * 4500)
            structure = (
                db.query(SalaryStructure)
                .filter(SalaryStructure.employee_id == employee.id)
                .first()
            )
            if not structure:
                structure = SalaryStructure(employee_id=employee.id)
                db.add(structure)
            structure.basic_salary = basic
            structure.hra = (basic * Decimal("0.20")).quantize(Decimal("0.01"))
            structure.allowances = Decimal("3500.00")
            structure.tax = (basic * Decimal("0.08")).quantize(Decimal("0.01"))
            structure.provident_fund = (basic * Decimal("0.05")).quantize(
                Decimal("0.01")
            )
            structure.insurance = Decimal("750.00")
            structure.other_deductions = Decimal("250.00")

            # Four completed/current payroll months and roughly four months of
            # weekday attendance make every demo dashboard meaningful.
            for month_offset in range(3, -1, -1):
                month_anchor = (
                    today.replace(day=1) - timedelta(days=month_offset * 31)
                ).replace(day=1)
                existing_payroll = (
                    db.query(PayrollRecord)
                    .filter(
                        PayrollRecord.employee_id == employee.id,
                        PayrollRecord.payroll_month == month_anchor,
                    )
                    .first()
                )
                if not existing_payroll:
                    bonus = (
                        Decimal("1500.00") if month_offset == 0 else Decimal("500.00")
                    )
                    overtime = Decimal(employee_index * 225)
                    gross = (
                        structure.basic_salary
                        + structure.hra
                        + structure.allowances
                        + bonus
                        + overtime
                    )
                    deductions = (
                        structure.tax
                        + structure.provident_fund
                        + structure.insurance
                        + structure.other_deductions
                    )
                    db.add(
                        PayrollRecord(
                            employee_id=employee.id,
                            payroll_month=month_anchor,
                            basic_salary=structure.basic_salary,
                            hra=structure.hra,
                            allowances=structure.allowances,
                            bonus=bonus,
                            overtime=overtime,
                            tax=structure.tax,
                            provident_fund=structure.provident_fund,
                            insurance=structure.insurance,
                            other_deductions=structure.other_deductions,
                            gross_salary=gross,
                            total_deductions=deductions,
                            net_salary=gross - deductions,
                            status="paid" if month_offset else "processed",
                            payment_date=month_anchor + timedelta(days=27)
                            if month_offset
                            else None,
                            payment_reference=f"DEMO-{employee.employee_id}-{month_anchor:%Y%m}",
                            created_by=admin_user.id,
                            updated_by=admin_user.id,
                        )
                    )

            first_day = today - timedelta(days=119)
            for day_offset in range(120):
                work_date = first_day + timedelta(days=day_offset)
                if work_date.weekday() >= 5:
                    continue
                if (
                    db.query(Attendance)
                    .filter(
                        Attendance.employee_id == employee.id,
                        Attendance.date == work_date,
                    )
                    .first()
                ):
                    continue
                selector = (day_offset + employee_index * 3) % 23
                status = (
                    "absent"
                    if selector == 0
                    else "half_day"
                    if selector == 7
                    else "late"
                    if selector in (4, 13)
                    else "present"
                )
                check_in = None
                check_out = None
                if status != "absent":
                    start_hour, start_minute = (10, 5) if status == "late" else (9, 0)
                    check_in = datetime.combine(
                        work_date, time(start_hour, start_minute), tzinfo=timezone.utc
                    )
                    end_hour = 13 if status == "half_day" else 17
                    check_out = datetime.combine(
                        work_date, time(end_hour, 30), tzinfo=timezone.utc
                    )
                db.add(
                    Attendance(
                        employee_id=employee.id,
                        date=work_date,
                        check_in=check_in,
                        check_out=check_out,
                        status=status,
                        notes="Generated demonstration history",
                        created_by=admin_user.id,
                        updated_by=admin_user.id,
                    )
                )

            for leave_type, allocation in (("annual", 18), ("sick", 10), ("casual", 8)):
                balance = (
                    db.query(LeaveBalance)
                    .filter(
                        LeaveBalance.employee_id == employee.id,
                        LeaveBalance.leave_type == leave_type,
                    )
                    .first()
                )
                if not balance:
                    db.add(
                        LeaveBalance(
                            employee_id=employee.id,
                            leave_type=leave_type,
                            allocated_days=allocation,
                            used_days=2 if leave_type == "annual" else 1,
                        )
                    )

            if (
                not db.query(LeaveRequest)
                .filter(LeaveRequest.employee_id == employee.id)
                .first()
            ):
                demo_requests = [
                    (
                        "annual",
                        today - timedelta(days=72),
                        today - timedelta(days=71),
                        "Family celebration",
                        "approved",
                        "Approved",
                    ),
                    (
                        "sick",
                        today - timedelta(days=38),
                        today - timedelta(days=38),
                        "Medical appointment",
                        "approved",
                        "Take care",
                    ),
                    (
                        "casual",
                        today - timedelta(days=18),
                        today - timedelta(days=18),
                        "Personal errands",
                        "rejected",
                        "Team coverage unavailable",
                    ),
                    (
                        "annual",
                        today + timedelta(days=12),
                        today + timedelta(days=14),
                        "Planned family trip",
                        "pending",
                        None,
                    ),
                ]
                for (
                    leave_type,
                    start_date,
                    end_date,
                    reason,
                    request_status,
                    remarks,
                ) in demo_requests:
                    db.add(
                        LeaveRequest(
                            employee_id=employee.id,
                            leave_type=leave_type,
                            start_date=start_date,
                            end_date=end_date,
                            reason=reason,
                            status=request_status,
                            admin_remarks=remarks,
                            reviewed_by=admin_user.id
                            if request_status != "pending"
                            else None,
                            reviewed_at=datetime.now(timezone.utc)
                            if request_status != "pending"
                            else None,
                        )
                    )
        db.commit()
        print(
            "Demo seed complete: 1 admin, 5 employees, 4 payroll months, and 120 days of attendance are ready."
        )
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed()
