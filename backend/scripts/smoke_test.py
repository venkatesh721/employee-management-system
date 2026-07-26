"""Read-only post-deployment smoke tests for administrator and employee access."""

import os
import sys

import httpx


def required(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise RuntimeError(f"Set {name} before running the smoke test")
    return value


def login(client: httpx.Client, identifier: str, password: str, role: str) -> dict:
    response = client.post(
        "/api/auth/login",
        json={"identifier": identifier, "password": password, "role": role},
    )
    response.raise_for_status()
    return response.json()


def check(client: httpx.Client, path: str, token: str) -> None:
    response = client.get(path, headers={"Authorization": f"Bearer {token}"})
    response.raise_for_status()
    print(f"PASS {path}")


def main() -> int:
    api_url = required("SMOKE_API_URL").rstrip("/")
    with httpx.Client(base_url=api_url, timeout=20, follow_redirects=False) as client:
        ready = client.get("/health/ready")
        ready.raise_for_status()
        print("PASS /health/ready")

        admin = login(
            client,
            required("SMOKE_ADMIN_IDENTIFIER"),
            required("SMOKE_ADMIN_PASSWORD"),
            "admin",
        )
        for path in (
            "/api/auth/me",
            "/api/dashboard/stats",
            "/api/employees?size=1",
            "/api/departments",
            "/api/attendance?size=1",
            "/api/payroll",
            "/api/leaves",
        ):
            check(client, path, admin["access_token"])

        employee = login(
            client,
            required("SMOKE_EMPLOYEE_IDENTIFIER"),
            required("SMOKE_EMPLOYEE_PASSWORD"),
            "employee",
        )
        for path in (
            "/api/auth/me",
            "/api/dashboard/employee",
            "/api/attendance/today",
            "/api/attendance/summary",
            "/api/payroll",
            "/api/leaves",
            "/api/leaves/balances",
        ):
            check(client, path, employee["access_token"])

    print("Post-deployment admin and employee smoke tests passed.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (RuntimeError, httpx.HTTPError) as exc:
        print(f"FAIL {exc}", file=sys.stderr)
        raise SystemExit(1)
