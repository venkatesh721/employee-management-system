# API Documentation

Base path: `/api`. Except for login, all endpoints require an `Authorization: Bearer <JWT>` header.

## Authentication

| Method | Endpoint | Access | Purpose |
|---|---|---|---|
| POST | `/auth/login` | Public | Authenticate email/username with selected role |
| POST | `/auth/register-employee` | Public | Register an Employee-only account |
| POST | `/auth/forgot-password` | Public | Request a generic reset response |
| POST | `/auth/reset-password` | Public | Consume a single-use reset token |
| POST | `/auth/logout` | Authenticated | End the client session |
| GET | `/auth/me` | Authenticated | Current sanitized user |
| PUT | `/auth/me` | Authenticated | Update own account profile/password |
| POST | `/auth/register` | Admin | Create a basic employee-role user |

Login errors: `401` invalid credentials, `403` inactive/wrong-role account, `422` invalid input. Registration duplicates return `409`.

## Employees

| Method | Endpoint | Access |
|---|---|---|
| GET/POST | `/employees` | Admin |
| GET | `/employees/me` | Authenticated employee |
| GET/PUT/DELETE | `/employees/{uuid}` | Admin |

Creating an employee creates a linked login account. `DELETE` is a recoverable soft delete: it sets employee status to `terminated` and disables login.

## Departments

`GET`, `POST`, `PUT`, and `DELETE` under `/departments` are admin-only.

## Attendance

- Admin list requests can see all records.
- Employee list, today, summary, check-in, and check-out requests are automatically scoped to the employee linked to the current account.
- Employees cannot update another employee’s attendance by changing request IDs.

## Dashboards and reporting

- `/dashboard/stats`, `/attendance-chart`, `/department-distribution`, `/recent-employees`: admin-only.
- `/dashboard/employee`: authenticated employee self-service summary.

## Workforce insights

`POST /insights/workforce` is admin-only.

```json
{ "focus": "attendance risk and capacity" }
```

The response contains `insights`, `source`, and aggregate `metrics`. `source` is either `ai` or `rules-based fallback`.

## Audit logs

`GET /audit-logs?limit=50` is admin-only and returns recent login, employee mutation, and insight-generation activity.

The authoritative interactive schema is generated at `/docs` and `/openapi.json`.
