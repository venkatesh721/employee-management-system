import uuid

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import Base, get_db
from app.core.security import hash_password
from app.main import app
from app.models.employee import Employee
from app.models.user import User


@pytest.fixture()
def client():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSession = sessionmaker(bind=engine, autocommit=False, autoflush=False)
    Base.metadata.create_all(engine)
    db = TestingSession()

    admin = User(
        id=uuid.uuid4(),
        email="admin@example.com",
        username="test_admin",
        hashed_password=hash_password("AdminTest123!"),
        full_name="Test Admin",
        role="admin",
        is_active=True,
        is_superuser=True,
    )
    employee_user = User(
        id=uuid.uuid4(),
        email="employee@example.com",
        username="test_employee",
        hashed_password=hash_password("EmployeeTest123!"),
        full_name="Test Employee",
        role="employee",
        is_active=True,
    )
    inactive = User(
        id=uuid.uuid4(),
        email="inactive@example.com",
        username="test_inactive",
        hashed_password=hash_password("InactiveTest123!"),
        full_name="Inactive Employee",
        role="employee",
        is_active=False,
    )
    db.add_all([admin, employee_user, inactive])
    db.flush()
    db.add(
        Employee(
            id=uuid.uuid4(),
            employee_id="EMP900",
            user_id=employee_user.id,
            first_name="Test",
            last_name="Employee",
            email=employee_user.email,
            position="Engineer",
            status="active",
        )
    )
    db.commit()
    db.close()

    def override_db():
        session = TestingSession()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
    Base.metadata.drop_all(engine)


def login_headers(client, identifier, password, role=None):
    selected_role = role or ("admin" if identifier.startswith("admin") else "employee")
    response = client.post(
        "/api/auth/login",
        json={"identifier": identifier, "password": password, "role": selected_role},
    )
    assert response.status_code == 200, response.text
    return {"Authorization": f"Bearer {response.json()['access_token']}"}
