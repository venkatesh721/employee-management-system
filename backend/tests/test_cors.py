import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.core.middleware import ProductionMiddleware
from app.main import app

PERMANENT_ORIGINS = [
    "http://localhost:5173",
    "https://employee-management-system-xi-three.vercel.app",
]
PREVIEW_ORIGIN = (
    "https://employee-management-system-kjvdlc495-venkatesh721s-projects.vercel.app"
)


def preflight(client, origin: str):
    return client.options(
        "/api/auth/login",
        headers={
            "Origin": origin,
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "content-type",
        },
    )


def test_cors_is_outermost_middleware():
    middleware_names = [middleware.cls.__name__ for middleware in app.user_middleware]

    assert middleware_names.index("CORSMiddleware") < middleware_names.index(
        "ProductionMiddleware"
    )


@pytest.mark.parametrize("origin", [*PERMANENT_ORIGINS, PREVIEW_ORIGIN])
def test_login_preflight_returns_cors_headers(client, origin):
    response = preflight(client, origin)

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == origin
    assert response.headers["access-control-allow-credentials"] == "true"
    assert "POST" in response.headers["access-control-allow-methods"]


@pytest.mark.parametrize("origin", PERMANENT_ORIGINS)
def test_login_response_contains_cors_headers(client, origin):
    response = client.post(
        "/api/auth/login",
        headers={"Origin": origin},
        json={
            "identifier": "admin@example.com",
            "password": "AdminTest123!",
            "role": "admin",
        },
    )

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == origin
    assert response.headers["access-control-allow-credentials"] == "true"


def test_unknown_origin_is_not_allowed(client):
    response = preflight(client, "https://attacker.example.com")

    assert response.status_code == 400
    assert "access-control-allow-origin" not in response.headers


def test_production_middleware_does_not_modify_options():
    inner_app = FastAPI()
    inner_app.add_middleware(ProductionMiddleware)

    @inner_app.options("/probe")
    def options_probe():
        return {"status": "ok"}

    with TestClient(inner_app) as inner_client:
        response = inner_client.options("/probe")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
    assert "x-request-id" not in response.headers
    assert "x-content-type-options" not in response.headers
