from datetime import timedelta

from app.core.security import create_access_token
from tests.conftest import login_headers


def test_successful_admin_login(client):
    response = client.post(
        "/api/auth/login",
        json={
            "identifier": "admin@example.com",
            "password": "AdminTest123!",
            "role": "admin",
        },
    )
    assert response.status_code == 200
    assert response.json()["user"]["role"] == "admin"
    assert "access_token" in response.json()


def test_successful_employee_login(client):
    response = client.post(
        "/api/auth/login",
        json={
            "identifier": "test_employee",
            "password": "EmployeeTest123!",
            "role": "employee",
        },
    )
    assert response.status_code == 200
    assert response.json()["user"]["role"] == "employee"


def test_invalid_login(client):
    response = client.post(
        "/api/auth/login",
        json={
            "identifier": "employee@example.com",
            "password": "wrong-password",
            "role": "employee",
        },
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid email/username or password"


def test_inactive_user_cannot_login(client):
    response = client.post(
        "/api/auth/login",
        json={
            "identifier": "inactive@example.com",
            "password": "InactiveTest123!",
            "role": "employee",
        },
    )
    assert response.status_code == 403
    assert response.json()["detail"] == "User account is inactive"


def test_admin_can_access_admin_api(client):
    headers = login_headers(client, "admin@example.com", "AdminTest123!")
    assert client.get("/api/dashboard/stats", headers=headers).status_code == 200


def test_employee_is_blocked_from_admin_api(client):
    headers = login_headers(client, "employee@example.com", "EmployeeTest123!")
    response = client.get("/api/employees", headers=headers)
    assert response.status_code == 403


def test_employee_can_access_allowed_api(client):
    headers = login_headers(client, "employee@example.com", "EmployeeTest123!")
    response = client.get("/api/dashboard/employee", headers=headers)
    assert response.status_code == 200
    assert response.json()["employee"]["employee_id"] == "EMP900"


def test_ai_insight_success_with_mock(client, monkeypatch):
    headers = login_headers(client, "admin@example.com", "AdminTest123!")
    monkeypatch.setattr(
        "app.api.routes.insights.generate_insights",
        lambda metrics, focus: (["Mocked actionable workforce insight"], "ai"),
    )
    response = client.post(
        "/api/insights/workforce", headers=headers, json={"focus": "retention"}
    )
    assert response.status_code == 200
    assert response.json()["source"] == "ai"
    assert response.json()["insights"] == ["Mocked actionable workforce insight"]


def test_insight_input_validation_and_employee_denial(client):
    admin_headers = login_headers(client, "admin@example.com", "AdminTest123!")
    assert (
        client.post(
            "/api/insights/workforce",
            headers=admin_headers,
            json={"focus": "x" * 301},
        ).status_code
        == 422
    )
    employee_headers = login_headers(client, "employee@example.com", "EmployeeTest123!")
    assert (
        client.post(
            "/api/insights/workforce", headers=employee_headers, json={"focus": ""}
        ).status_code
        == 403
    )


def test_missing_authentication_returns_401(client):
    response = client.get("/api/auth/me")
    assert response.status_code == 401
    assert response.json()["detail"] == "Authentication required"


def test_expired_token_returns_401(client):
    token = create_access_token(
        {"sub": "00000000-0000-0000-0000-000000000000"},
        expires_delta=timedelta(seconds=-1),
    )
    response = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid or expired token"
