import uuid
from datetime import datetime, timedelta, timezone
from urllib.parse import parse_qs, urlparse

from app.core.database import get_db
from app.main import app
from app.models.password_reset_token import PasswordResetToken
from app.models.user import User
from app.services.password_reset import hash_reset_token

STRONG_PASSWORD = "Employee@123"


def registration_payload(**overrides):
    payload = {
        "full_name": "Registered Employee",
        "username": "registered_employee",
        "email": "registered.employee@example.com",
        "phone": "+91 9000000000",
        "password": STRONG_PASSWORD,
        "confirm_password": STRONG_PASSWORD,
        "accept_terms": True,
    }
    payload.update(overrides)
    return payload


def test_wrong_role_login_is_rejected(client):
    response = client.post(
        "/api/auth/login",
        json={
            "identifier": "employee@example.com",
            "password": "EmployeeTest123!",
            "role": "admin",
        },
    )
    assert response.status_code == 403
    assert response.json()["detail"] == (
        "This account is not registered as an Administrator."
    )


def test_employee_registration_and_public_admin_prevention(client):
    response = client.post("/api/auth/register-employee", json=registration_payload())
    assert response.status_code == 201
    assert response.json()["role"] == "employee"

    login = client.post(
        "/api/auth/login",
        json={
            "identifier": "registered_employee",
            "password": STRONG_PASSWORD,
            "role": "employee",
        },
    )
    assert login.status_code == 200

    admin_attempt = registration_payload(
        username="admin_attempt",
        email="admin.attempt@example.com",
        role="admin",
    )
    blocked = client.post("/api/auth/register-employee", json=admin_attempt)
    assert blocked.status_code == 422


def test_registration_normalizes_email_and_login_accepts_spaces_and_case(client):
    response = client.post(
        "/api/auth/register-employee",
        json=registration_payload(
            username="normalized_employee",
            email="  Normalized.Employee@Example.COM  ",
        ),
    )
    assert response.status_code == 201, response.text
    assert response.json()["email"] == "normalized.employee@example.com"

    login = client.post(
        "/api/auth/login",
        json={
            "identifier": "  NORMALIZED.EMPLOYEE@EXAMPLE.COM  ",
            "password": STRONG_PASSWORD,
            "role": "employee",
        },
    )
    assert login.status_code == 200, login.text

    assert login.json()["user"]["role"] == "employee"


def test_admin_created_employee_can_login_with_normalized_email(client):
    admin_login = client.post(
        "/api/auth/login",
        json={
            "identifier": "admin@example.com",
            "password": "AdminTest123!",
            "role": "admin",
        },
    )
    assert admin_login.status_code == 200
    headers = {
        "Authorization": f"Bearer {admin_login.json()['access_token']}",
    }
    created = client.post(
        "/api/employees",
        headers=headers,
        json={
            "first_name": "Admin",
            "last_name": "Created",
            "email": "  Admin.Created@Example.COM  ",
            "password": "AdminCreated123!",
            "role": "employee",
            "status": "active",
        },
    )
    assert created.status_code == 201, created.text
    assert created.json()["email"] == "admin.created@example.com"

    login = client.post(
        "/api/auth/login",
        json={
            "identifier": "  ADMIN.CREATED@EXAMPLE.COM ",
            "password": "AdminCreated123!",
            "role": "employee",
        },
    )
    assert login.status_code == 200, login.text

    updated = client.put(
        f"/api/employees/{created.json()['id']}",
        headers=headers,
        json={"password": "UpdatedByAdmin123!"},
    )
    assert updated.status_code == 200, updated.text

    old_password_login = client.post(
        "/api/auth/login",
        json={
            "identifier": "admin.created@example.com",
            "password": "AdminCreated123!",
            "role": "employee",
        },
    )
    assert old_password_login.status_code == 401

    updated_password_login = client.post(
        "/api/auth/login",
        json={
            "identifier": "admin.created@example.com",
            "password": "UpdatedByAdmin123!",
            "role": "employee",
        },
    )
    assert updated_password_login.status_code == 200


def test_login_password_and_both_role_mismatch_statuses(client):
    invalid_password = client.post(
        "/api/auth/login",
        json={
            "identifier": "employee@example.com",
            "password": "IncorrectPassword123!",
            "role": "employee",
        },
    )
    assert invalid_password.status_code == 401
    assert invalid_password.json()["detail"] == "Invalid email/username or password"

    employee_as_admin = client.post(
        "/api/auth/login",
        json={
            "identifier": "employee@example.com",
            "password": "EmployeeTest123!",
            "role": "admin",
        },
    )
    assert employee_as_admin.status_code == 403
    assert "Administrator" in employee_as_admin.json()["detail"]

    admin_as_employee = client.post(
        "/api/auth/login",
        json={
            "identifier": "admin@example.com",
            "password": "AdminTest123!",
            "role": "employee",
        },
    )
    assert admin_as_employee.status_code == 403
    assert "Employee" in admin_as_employee.json()["detail"]


def test_registration_duplicate_and_password_validation(client):
    assert (
        client.post(
            "/api/auth/register-employee", json=registration_payload()
        ).status_code
        == 201
    )
    duplicate_email = client.post(
        "/api/auth/register-employee",
        json=registration_payload(username="different_username"),
    )
    assert duplicate_email.status_code == 409

    duplicate_username = client.post(
        "/api/auth/register-employee",
        json=registration_payload(email="different@example.com"),
    )
    assert duplicate_username.status_code == 409

    weak = client.post(
        "/api/auth/register-employee",
        json=registration_payload(
            username="weak_user",
            email="weak@example.com",
            password="weakpass",
            confirm_password="weakpass",
        ),
    )
    assert weak.status_code == 422


def test_forgot_password_is_generic_for_known_and_unknown_email(client, monkeypatch):
    delivered = []
    monkeypatch.setattr(
        "app.api.routes.auth.deliver_reset_link",
        lambda recipient, url: delivered.append((recipient, url)),
    )
    known = client.post(
        "/api/auth/forgot-password", json={"email": "employee@example.com"}
    )
    unknown = client.post(
        "/api/auth/forgot-password", json={"email": "unknown@example.com"}
    )
    assert known.status_code == unknown.status_code == 200
    assert known.json() == unknown.json()
    assert len(delivered) == 1


def test_valid_reset_token_is_single_use(client, monkeypatch):
    delivered = []
    monkeypatch.setattr(
        "app.api.routes.auth.deliver_reset_link",
        lambda recipient, url: delivered.append(url),
    )
    client.post("/api/auth/forgot-password", json={"email": "employee@example.com"})
    token = parse_qs(urlparse(delivered[0]).query)["token"][0]
    payload = {
        "token": token,
        "password": "NewPassword@123",
        "confirm_password": "NewPassword@123",
    }
    assert client.post("/api/auth/reset-password", json=payload).status_code == 200
    assert client.post("/api/auth/reset-password", json=payload).status_code == 400
    assert (
        client.post(
            "/api/auth/login",
            json={
                "identifier": "employee@example.com",
                "password": "NewPassword@123",
                "role": "employee",
            },
        ).status_code
        == 200
    )


def test_expired_reset_token_is_rejected(client):
    session_generator = app.dependency_overrides[get_db]()
    db = next(session_generator)
    user = db.query(User).filter(User.email == "employee@example.com").first()
    token = "expired-token-" + uuid.uuid4().hex
    db.add(
        PasswordResetToken(
            id=uuid.uuid4(),
            user_id=user.id,
            token_hash=hash_reset_token(token),
            expires_at=datetime.now(timezone.utc) - timedelta(minutes=1),
        )
    )
    db.commit()
    db.close()
    session_generator.close()

    response = client.post(
        "/api/auth/reset-password",
        json={
            "token": token,
            "password": "AnotherPassword@123",
            "confirm_password": "AnotherPassword@123",
        },
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Password reset token has expired"
