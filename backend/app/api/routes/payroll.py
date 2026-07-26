import uuid
from datetime import date
from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException, Response, status
from pydantic import BaseModel
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user, require_admin
from app.models.employee import Employee
from app.models.payroll import PayrollAuditLog, PayrollRecord, SalaryStructure
from app.models.user import User

router = APIRouter(prefix="/api/payroll", tags=["Payroll"])
ZERO = Decimal("0.00")


class SalaryInput(BaseModel):
    basic_salary: Decimal = ZERO
    hra: Decimal = ZERO
    allowances: Decimal = ZERO
    tax: Decimal = ZERO
    provident_fund: Decimal = ZERO
    insurance: Decimal = ZERO
    other_deductions: Decimal = ZERO


class PayrollInput(SalaryInput):
    employee_id: str
    payroll_month: date
    bonus: Decimal = ZERO
    overtime: Decimal = ZERO
    status: str = "draft"
    payment_date: date | None = None
    payment_reference: str | None = None


def own_employee(db, user):
    employee = db.query(Employee).filter(Employee.user_id == user.id).first()
    if not employee:
        raise HTTPException(
            404,
            "No employee profile is linked to this account. Contact an administrator.",
        )
    return employee


def serialize(r):
    return {c.name: getattr(r, c.name) for c in r.__table__.columns}


@router.put("/structures/{employee_id}")
def upsert_structure(
    employee_id: str,
    payload: SalaryInput,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    employee = db.query(Employee).filter(Employee.id == uuid.UUID(employee_id)).first()
    if not employee:
        raise HTTPException(404, "Employee not found")
    row = (
        db.query(SalaryStructure)
        .filter(SalaryStructure.employee_id == employee.id)
        .first()
    )
    if not row:
        row = SalaryStructure(employee_id=employee.id)
        db.add(row)
    for key, value in payload.model_dump().items():
        setattr(row, key, value)
    db.commit()
    db.refresh(row)
    return serialize(row)


@router.post("", status_code=status.HTTP_201_CREATED)
def create_payroll(
    payload: PayrollInput,
    db: Session = Depends(get_db),
    user: User = Depends(require_admin),
):
    employee = (
        db.query(Employee).filter(Employee.id == uuid.UUID(payload.employee_id)).first()
    )
    if not employee:
        raise HTTPException(404, "Employee not found")
    values = payload.model_dump()
    month = payload.payroll_month.replace(day=1)
    values["payroll_month"] = month
    gross = (
        payload.basic_salary
        + payload.hra
        + payload.allowances
        + payload.bonus
        + payload.overtime
    )
    deductions = (
        payload.tax
        + payload.provident_fund
        + payload.insurance
        + payload.other_deductions
    )
    row = PayrollRecord(
        id=uuid.uuid4(),
        **values,
        gross_salary=gross,
        total_deductions=deductions,
        net_salary=gross - deductions,
        created_by=user.id,
        updated_by=user.id,
    )
    db.add(row)
    try:
        db.flush()
    except IntegrityError:
        db.rollback()
        raise HTTPException(409, "Payroll already exists for this employee and month")
    db.add(PayrollAuditLog(payroll_id=row.id, user_id=user.id, action="create"))
    db.commit()
    db.refresh(row)
    return serialize(row)


@router.get("")
def list_payroll(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    query = db.query(PayrollRecord)
    if user.role != "admin" and not user.is_superuser:
        query = query.filter(PayrollRecord.employee_id == own_employee(db, user).id)
    return [
        serialize(r) for r in query.order_by(PayrollRecord.payroll_month.desc()).all()
    ]


def _owned_record(record_id, db, user):
    row = (
        db.query(PayrollRecord).filter(PayrollRecord.id == uuid.UUID(record_id)).first()
    )
    if not row:
        raise HTTPException(404, "Payroll record not found")
    if (
        user.role != "admin"
        and not user.is_superuser
        and row.employee_id != own_employee(db, user).id
    ):
        raise HTTPException(403, "You cannot access another employee's payroll")
    return row


@router.get("/{record_id}")
def get_payroll(
    record_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return serialize(_owned_record(record_id, db, user))


@router.get("/{record_id}/payslip")
def payslip(
    record_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    row = _owned_record(record_id, db, user)
    employee = row.employee
    text = f"GLOBALCO EMS PAYSLIP\\nEmployee: {employee.first_name} {employee.last_name}\\nMonth: {row.payroll_month:%B %Y}\\nGross: {row.gross_salary}\\nDeductions: {row.total_deductions}\\nNet Salary: {row.net_salary}\\nStatus: {row.status}"
    safe = (
        text.replace("\\", "\\\\")
        .replace("(", "\\(")
        .replace(")", "\\)")
        .replace("\n", ") Tj 0 -16 Td (")
    )
    stream = f"BT /F1 12 Tf 50 750 Td ({safe}) Tj ET".encode()
    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
        b"<< /Length %d >>\nstream\n%s\nendstream" % (len(stream), stream),
    ]
    pdf = bytearray(b"%PDF-1.4\n")
    offsets = []
    for i, obj in enumerate(objects, 1):
        offsets.append(len(pdf))
        pdf += f"{i} 0 obj\n".encode() + obj + b"\nendobj\n"
    xref = len(pdf)
    pdf += f"xref\n0 {len(objects) + 1}\n0000000000 65535 f \n".encode()
    for off in offsets:
        pdf += f"{off:010d} 00000 n \n".encode()
    pdf += f"trailer << /Size {len(objects) + 1} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF".encode()
    return Response(
        bytes(pdf),
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="payslip-{row.payroll_month}.pdf"'
        },
    )
