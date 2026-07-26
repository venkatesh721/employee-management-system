import uuid

import pytest
from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.api.routes.auth import login
from app.core.database import Base
from app.core.security import hash_password
from app.models.user import User
from app.schemas.auth import LoginRequest
from app.services.administrator import ensure_default_administrator


@pytest.fixture()
def db():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    with Session() as session:
        yield session
    Base.metadata.drop_all(engine)


def test_default_administrator_is_created_once_and_can_login(db):
    assert ensure_default_administrator(db) is True
    assert ensure_default_administrator(db) is False

    administrators = db.query(User).filter(User.role == "admin").all()
    assert len(administrators) == 1
    administrator = administrators[0]
    assert administrator.username == "venkatesh"
    assert administrator.is_superuser is True
    assert administrator.is_active is True

    response = login(
        LoginRequest(
            identifier="venkatesh",
            password="Admin@123",
            role="admin",
        ),
        db,
    )
    assert response.user.id == administrator.id
    assert response.user.role == "admin"


def test_existing_administrator_prevents_default_creation(db):
    existing = User(
        id=uuid.uuid4(),
        email="owner@example.com",
        username="owner",
        hashed_password=hash_password("OwnerPassword123!"),
        full_name="Existing Owner",
        role="admin",
        is_superuser=True,
        is_active=True,
    )
    db.add(existing)
    db.commit()

    assert ensure_default_administrator(db) is False
    assert db.query(User).filter(User.role == "admin").count() == 1
    assert db.query(User).filter(User.username == "venkatesh").first() is None


def test_database_rejects_second_administrator(db):
    assert ensure_default_administrator(db) is True
    db.add(
        User(
            id=uuid.uuid4(),
            email="second-admin@example.com",
            username="second_admin",
            hashed_password=hash_password("SecondAdmin123!"),
            full_name="Second Admin",
            role="admin",
            is_superuser=True,
            is_active=True,
        )
    )

    with pytest.raises(IntegrityError):
        db.commit()
    db.rollback()


def test_employee_api_rejects_admin_creation_and_promotion(client):
    login_response = client.post(
        "/api/auth/login",
        json={
            "identifier": "admin@example.com",
            "password": "AdminTest123!",
            "role": "admin",
        },
    )
    headers = {"Authorization": f"Bearer {login_response.json()['access_token']}"}
    create_response = client.post(
        "/api/employees",
        headers=headers,
        json={
            "first_name": "Blocked",
            "last_name": "Administrator",
            "email": "blocked-admin@example.com",
            "password": "BlockedAdmin123!",
            "role": "admin",
        },
    )
    assert create_response.status_code == 400
    assert "cannot be created" in create_response.json()["detail"]

    employee_response = client.get("/api/employees?size=1", headers=headers)
    employee_id = employee_response.json()["items"][0]["id"]
    promote_response = client.put(
        f"/api/employees/{employee_id}",
        headers=headers,
        json={"role": "admin"},
    )
    assert promote_response.status_code == 400
    assert "cannot be promoted" in promote_response.json()["detail"]
