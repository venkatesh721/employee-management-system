# Architecture

## Components

- `frontend/src/contexts/AuthContext.jsx` owns session state and current-user restoration.
- `ProtectedRoute` enforces route roles; `Sidebar` derives navigation from the current role.
- `frontend/src/services` centralizes Axios API calls and bearer-token handling.
- FastAPI routers expose authentication, employees, departments, attendance, dashboards, insights, and audit APIs.
- `get_current_user`, `require_roles`, and `require_admin` are reusable security dependencies.
- SQLAlchemy models persist identity, workforce, attendance, organizational, and audit data.
- Password-reset tokens are random, stored as hashes, expire, and are invalidated after one use.

## Authorization flow

```text
Request
  -> HTTPBearer parses token
  -> JWT signature/expiry validation (401 on failure)
  -> user lookup and active check
  -> require_roles dependency (403 on role mismatch)
  -> route business logic
  -> scoped database query
```

Frontend guards improve navigation but are not trusted as the security boundary.

## Data ownership

`employees.user_id` links the login identity to the workforce profile. Employee attendance queries derive the permitted employee UUID from the authenticated user; client-provided identifiers cannot broaden access. Admin queries use reusable admin dependencies.

## AI insights

Only aggregate counts are sent to the optional provider. No names, emails, salaries, or attendance-level records are included. Input is length validated, output is parsed as structured JSON, calls use a timeout, and failures return rules-based recommendations.

## Audit design

Mutation/login/insight events record actor UUID, action, resource type/ID, safe JSON details, and timestamp. Passwords and tokens are never logged.
