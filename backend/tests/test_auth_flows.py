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
