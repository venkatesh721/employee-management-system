from tests.conftest import login_headers


def test_admin_management_and_reporting_flow(client):
    headers = login_headers(client, "admin@example.com", "AdminTest123!")

    created_department = client.post(
        "/api/departments",
        headers=headers,
        json={"name": "Verification", "description": "Integration verification"},
    )
    assert created_department.status_code == 201
    department_id = created_department.json()["id"]

    updated_department = client.put(
        f"/api/departments/{department_id}",
        headers=headers,
        json={"description": "Updated verification department"},
    )
    assert updated_department.status_code == 200

    disposable = client.post(
        "/api/departments",
        headers=headers,
        json={"name": "Disposable", "description": "Delete verification"},
    )
    assert disposable.status_code == 201
    assert (
        client.delete(
            f"/api/departments/{disposable.json()['id']}", headers=headers
        ).status_code
        == 204
    )

    employee_payload = {
        "first_name": "Flow",
        "last_name": "Verifier",
        "email": "flow.verifier@example.com",
        "password": "FlowVerifier123!",
        "role": "employee",
        "department_id": department_id,
        "position": "QA Engineer",
        "status": "active",
    }
    created_employee = client.post(
        "/api/employees", headers=headers, json=employee_payload
    )
    assert created_employee.status_code == 201, created_employee.text
    employee = created_employee.json()
    assert employee["employee_id"].startswith("EMP")
    assert employee["role"] == "employee"

    search = client.get(
        "/api/employees",
        headers=headers,
        params={"search": "flow.verifier@example.com"},
    )
    assert search.status_code == 200
    assert search.json()["total"] == 1

    detail = client.get(f"/api/employees/{employee['id']}", headers=headers)
    assert detail.status_code == 200

    update = client.put(
        f"/api/employees/{employee['id']}",
        headers=headers,
        json={"position": "Senior QA Engineer", "role": "employee"},
    )
    assert update.status_code == 200
    assert update.json()["position"] == "Senior QA Engineer"

    employee_login = client.post(
        "/api/auth/login",
        json={
            "identifier": "flow.verifier@example.com",
            "password": "FlowVerifier123!",
            "role": "employee",
        },
    )
    assert employee_login.status_code == 200

    insight = client.post(
        "/api/insights/workforce",
        headers=headers,
        json={"focus": "attendance and capacity"},
    )
    assert insight.status_code == 200
    assert insight.json()["source"] in {"ai", "rules-based fallback"}
    assert insight.json()["insights"]

    audit = client.get("/api/audit-logs", headers=headers)
    assert audit.status_code == 200
    assert any(log["resource_type"] == "employee" for log in audit.json())

    deactivate = client.delete(f"/api/employees/{employee['id']}", headers=headers)
    assert deactivate.status_code == 204
    blocked_login = client.post(
        "/api/auth/login",
        json={
            "identifier": "flow.verifier@example.com",
            "password": "FlowVerifier123!",
            "role": "employee",
        },
    )
    assert blocked_login.status_code == 403


def test_employee_self_service_and_backend_scope(client):
    headers = login_headers(client, "employee@example.com", "EmployeeTest123!")

    assert client.get("/api/dashboard/employee", headers=headers).status_code == 200
    own_profile = client.get("/api/employees/me", headers=headers)
    assert own_profile.status_code == 200
    assert own_profile.json()["employee_id"] == "EMP900"

    check_in = client.post("/api/attendance", headers=headers, json={"notes": "Test"})
    assert check_in.status_code == 403

    assert client.get("/api/attendance", headers=headers).status_code == 200
    assert client.get("/api/attendance/summary", headers=headers).status_code == 200
    assert client.get("/api/departments", headers=headers).status_code == 403
    assert client.get("/api/audit-logs", headers=headers).status_code == 403
