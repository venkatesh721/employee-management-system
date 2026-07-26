from datetime import date, timedelta
from decimal import Decimal
from tests.conftest import login_headers


def employee_id(client, admin):
    return client.get("/api/employees", headers=admin).json()["items"][0]["id"]


def test_admin_attendance_duplicate_and_employee_read_only(client):
    admin = login_headers(client, "admin@example.com", "AdminTest123!")
    employee = login_headers(client, "employee@example.com", "EmployeeTest123!")
    payload = {
        "employee_id": employee_id(client, admin),
        "date": str(date.today()),
        "check_in": f"{date.today()}T09:00:00",
        "check_out": f"{date.today()}T17:00:00",
        "status": "present",
    }
    created = client.post("/api/attendance", headers=admin, json=payload)
    assert created.status_code == 201, created.text
    assert created.json()["working_hours"] == 8
    assert (
        client.post("/api/attendance", headers=admin, json=payload).status_code == 409
    )
    assert (
        client.post("/api/attendance", headers=employee, json=payload).status_code
        == 403
    )
    assert (
        client.put(
            f"/api/attendance/{created.json()['id']}",
            headers=employee,
            json={"status": "late", "audit_reason": "test"},
        ).status_code
        == 403
    )
    assert client.get("/api/attendance", headers=employee).json()["total"] == 1


def test_payroll_decimal_formula_duplicate_and_ownership(client):
    admin = login_headers(client, "admin@example.com", "AdminTest123!")
    employee = login_headers(client, "employee@example.com", "EmployeeTest123!")
    payload = {
        "employee_id": employee_id(client, admin),
        "payroll_month": "2026-07-01",
        "basic_salary": "10000.10",
        "hra": "1000.20",
        "allowances": "500.30",
        "bonus": "200.40",
        "overtime": "100.50",
        "tax": "500.10",
        "provident_fund": "300.20",
        "insurance": "100.30",
        "other_deductions": "50.40",
        "status": "processed",
    }
    r = client.post("/api/payroll", headers=admin, json=payload)
    assert r.status_code == 201, r.text
    assert Decimal(str(r.json()["gross_salary"])) == Decimal("11801.50")
    assert Decimal(str(r.json()["total_deductions"])) == Decimal("951.00")
    assert client.post("/api/payroll", headers=admin, json=payload).status_code == 409
    own = client.get("/api/payroll", headers=employee)
    assert own.status_code == 200 and len(own.json()) == 1
    assert (
        client.get(f"/api/payroll/{r.json()['id']}/payslip", headers=employee).headers[
            "content-type"
        ]
        == "application/pdf"
    )


def test_leave_approval_creates_on_leave_attendance(client):
    employee = login_headers(client, "employee@example.com", "EmployeeTest123!")
    admin = login_headers(client, "admin@example.com", "AdminTest123!")
    tomorrow = date.today() + timedelta(days=1)
    payload = {
        "leave_type": "annual",
        "start_date": f"{tomorrow}T00:00:00",
        "end_date": f"{tomorrow}T00:00:00",
        "reason": "Personal",
    }
    request = client.post("/api/leaves", headers=employee, json=payload)
    assert request.status_code == 201, request.text
    approved = client.put(
        f"/api/leaves/{request.json()['id']}/review",
        headers=admin,
        json={"status": "approved", "remarks": "Approved"},
    )
    assert approved.status_code == 200
    records = client.get(
        "/api/attendance",
        headers=employee,
        params={"date_from": tomorrow, "date_to": tomorrow},
    ).json()["items"]
    assert records[0]["status"] == "on_leave"


def test_ai_authorization_and_safe_assistant(client):
    employee = login_headers(client, "employee@example.com", "EmployeeTest123!")
    admin = login_headers(client, "admin@example.com", "AdminTest123!")
    assert client.get("/api/ai/attendance-risk", headers=employee).status_code == 200
    assert client.get("/api/ai/anomalies", headers=employee).status_code == 403
    assert (
        client.post(
            "/api/ai/hr-assistant", headers=admin, json={"question": "drop table users"}
        ).status_code
        == 422
    )


def test_admin_attendance_correction_requires_audit_reason(client):
    admin = login_headers(client, "admin@example.com", "AdminTest123!")
    payload = {
        "employee_id": employee_id(client, admin),
        "date": "2026-06-15",
        "check_in": "2026-06-15T09:30:00",
        "check_out": "2026-06-15T17:30:00",
        "status": "late",
    }
    created = client.post("/api/attendance", headers=admin, json=payload)
    assert created.status_code == 201, created.text
    assert (
        client.put(
            f"/api/attendance/{created.json()['id']}",
            headers=admin,
            json={"status": "present"},
        ).status_code
        == 422
    )
    corrected = client.put(
        f"/api/attendance/{created.json()['id']}",
        headers=admin,
        json={"status": "present", "audit_reason": "Approved timesheet correction"},
    )
    assert corrected.status_code == 200
    assert corrected.json()["status"] == "present"


def test_policy_upload_and_cited_answer(client):
    admin = login_headers(client, "admin@example.com", "AdminTest123!")
    uploaded = client.post(
        "/api/policies",
        headers=admin,
        files={
            "file": (
                "leave-policy.md",
                b"# Annual Leave\nEmployees receive 18 annual leave days.",
                "text/markdown",
            )
        },
    )
    assert uploaded.status_code == 201, uploaded.text
    answer = client.post(
        "/api/policies/ask",
        headers=admin,
        json={"question": "How many annual leave days do employees receive?"},
    )
    assert answer.status_code == 200
    assert answer.json()["sources"][0]["document"] == "leave-policy.md"


def test_employee_deployment_workflow_and_cross_payroll_denial(client):
    admin = login_headers(client, "admin@example.com", "AdminTest123!")
    employee = login_headers(client, "employee@example.com", "EmployeeTest123!")

    dashboard = client.get("/api/dashboard/employee", headers=employee)
    assert dashboard.status_code == 200
    assert dashboard.json()["employee"]["employee_id"] == "EMP900"

    updated = client.put(
        "/api/auth/me",
        headers=employee,
        json={
            "full_name": "Test Employee Updated",
            "username": "test_employee",
            "email": "employee@example.com",
        },
    )
    assert updated.status_code == 200, updated.text
    assert updated.json()["full_name"] == "Test Employee Updated"
    own_profile = client.get("/api/employees/me", headers=employee)
    assert own_profile.status_code == 200
    assert own_profile.json()["first_name"] == "Test"

    other = client.post(
        "/api/employees",
        headers=admin,
        json={
            "first_name": "Other",
            "last_name": "Employee",
            "email": "other.employee@example.com",
            "password": "OtherEmployee123!",
            "role": "employee",
            "status": "active",
        },
    )
    assert other.status_code == 201, other.text
    other_payroll = client.post(
        "/api/payroll",
        headers=admin,
        json={
            "employee_id": other.json()["id"],
            "payroll_month": "2026-05-01",
            "basic_salary": "50000.00",
            "status": "processed",
        },
    )
    assert other_payroll.status_code == 201, other_payroll.text
    assert (
        client.get(
            f"/api/payroll/{other_payroll.json()['id']}", headers=employee
        ).status_code
        == 403
    )
    assert (
        client.get(
            f"/api/payroll/{other_payroll.json()['id']}/payslip", headers=employee
        ).status_code
        == 403
    )

    assert client.get("/api/attendance", headers=employee).status_code == 200
    assert (
        client.post(
            "/api/attendance",
            headers=employee,
            json={
                "employee_id": other.json()["id"],
                "date": "2026-05-01",
                "status": "present",
            },
        ).status_code
        == 403
    )
    assert client.get("/api/leaves", headers=employee).status_code == 200
    assert client.get("/api/leaves/balances", headers=employee).status_code == 200
    policy_answer = client.post(
        "/api/policies/ask",
        headers=employee,
        json={"question": "annual leave days"},
    )
    assert policy_answer.status_code == 200
