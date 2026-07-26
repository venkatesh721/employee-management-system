# GLOBALCO Employee Management System

A full-stack workforce operations application prepared for the GLOBALCO Software Engineer Technical Assessment.

## Business problem

Workforce information, attendance, account access, and operational reporting are often spread across disconnected tools. This makes it difficult to manage access securely, identify attendance risk, and give employees an appropriate self-service experience.

## Proposed solution

GLOBALCO EMS centralizes employee accounts, departments, attendance, dashboards, audit activity, and workforce insights. It uses backend-enforced role-based access so administrators and employees see only the data and actions appropriate to them.

The assessment edition also provides administrator-only attendance entry, fixed-precision payroll and PDF payslips, leave approval with attendance synchronization, explainable attendance/payroll risk signals, a safe HR natural-language assistant, and source-citing policy retrieval. Employee pages are ownership-scoped and read-only where required.

## Role matrix

| Capability | Administrator | Employee |
|---|---:|---:|
| Manage employee accounts/profiles | Yes | Own profile view/update only |
| Create/correct attendance | Yes | No |
| View attendance | All | Own only |
| Generate/manage payroll | Yes | No |
| View/download payslips | All | Own only |
| Leave requests | Review all | Apply/view own |
| HR analytics and anomaly alerts | Yes | Personal risk summary only |
| Policy assistant | Yes | Yes |

See [database schema](docs/DATABASE_SCHEMA.md), [AI features](docs/AI_FEATURES.md), and [security](docs/SECURITY.md).

## AI-powered business value

The admin Workforce Insights page analyzes current workforce and 30-day attendance metrics and returns concise operational recommendations. When `OPENAI_API_KEY` is configured, the backend requests structured AI recommendations without sending personal employee records. If the provider is unavailable or unconfigured, a deterministic rules-based engine produces useful fallback observations.

## Features

- Role-selected email/username login, JWT logout/current-user flow, bcrypt hashing, and inactive-user blocking
- Public Employee-only registration with strong-password validation
- Expiring, hashed, single-use password-reset tokens with SMTP/development delivery
- Backend and frontend RBAC for `admin` and `employee`
- Separate `/admin/dashboard` and `/employee/dashboard`
- Admin employee account creation, search, filtering, editing, role assignment, activation, and deactivation
- Department and attendance management
- Employee self-service profile and employee-scoped attendance
- Admin workforce analytics, AI insights, and audit logs
- Responsive navigation, loading and empty states, validation, notifications, and destructive-action confirmation
- Alembic migration, idempotent demo seed, automated tests, CI, and deployment configuration

## Permissions

| Capability | Admin | Employee |
|---|---:|---:|
| Admin dashboard and statistics | Yes | No |
| Employee dashboard | No | Yes |
| List/create/edit/deactivate employee accounts | Yes | No |
| Assign account roles | Yes | No |
| Manage departments | Yes | No |
| View all attendance | Yes | No |
| View/update own attendance | Yes | Yes |
| View/update own account profile | Yes | Yes |
| Generate workforce insights | Yes | No |
| View audit logs | Yes | No |

Unauthorized authenticated requests return `403`; missing, invalid, or expired tokens return `401`.

## Technology stack

- Frontend: React 18, React Router, Axios, Recharts, Vite
- Backend: FastAPI, SQLAlchemy, Pydantic, bcrypt, python-jose
- Database: SQLite locally; SQLAlchemy-compatible PostgreSQL for deployment
- Migration/testing: Alembic, pytest, HTTPX
- Quality/automation: ESLint, Ruff, GitHub Actions

## Architecture

```text
React UI -> Axios bearer token -> FastAPI routes
                                -> auth/RBAC dependencies
                                -> services (audit + insights)
                                -> SQLAlchemy -> SQLite/PostgreSQL
```

See [Architecture](docs/ARCHITECTURE.md) for the detailed flow.

## Database design

- `users`: login identity, phone, password hash, role, active/superuser flags, timestamps
- `password_reset_tokens`: token hash, owner, expiration, use time, and creation time
- `employees`: workforce profile linked to an optional user account
- `departments`: organizational units and manager relationship
- `attendance`: employee check-in/out records
- `audit_logs`: actor, action, resource, details, and timestamp

UUIDs are used internally. Employee-facing identifiers use values such as `EMP001`.

## Authentication flow

1. User selects Administrator or Employee and posts the selected role, email/username, and password to `POST /api/auth/login`.
2. Backend normalizes email, locates the user, checks bcrypt, and rejects inactive users.
3. Backend securely compares the selected role with the stored role and returns `403` for a wrong-role login.
4. Backend returns a signed expiring JWT and sanitized user object.
5. Axios sends the token using `Authorization: Bearer <token>`.
6. `/api/auth/me` restores the session after refresh.
7. The frontend redirects by role; backend dependencies independently enforce authorization.

## Employee registration

`/register-employee` creates Employee accounts only. The backend does not accept a role field, checks duplicate email/username, validates the email and strong password, hashes the password, creates a linked employee profile, and redirects successful registrations to Employee login.

## Forgot-password flow

1. `/forgot-password` accepts an email and always returns the same generic response.
2. The backend generates a cryptographically random token and stores only its SHA-256 hash.
3. The reset link is sent through configured SMTP. In development only, it is written to backend logs when SMTP is unavailable.
4. `/reset-password?token=...` accepts and confirms a strong password.
5. The backend rejects expired, invalid, or used tokens, hashes the new password, and invalidates every outstanding token for the account.

## Local installation

Prerequisites: Python 3.11+, Node.js 20+, npm.

```powershell
git clone <repository-url>
cd employee-management-system

cd backend
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
Copy-Item .env.example .env
alembic upgrade head
python seed_data.py
uvicorn app.main:app --reload --port 8000
```

In another terminal:

```powershell
cd frontend
npm ci
Copy-Item .env.example .env
npm run dev
```

Frontend: `http://localhost:3000`

API docs: `http://localhost:8000/docs`

## Environment variables

Backend:

| Variable | Required | Description |
|---|---:|---|
| `DATABASE_URL` | Yes | SQLAlchemy connection URL |
| `SECRET_KEY` | Yes in production | Long random JWT signing key |
| `ALGORITHM` | No | JWT algorithm, default `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | No | Token lifetime |
| `PASSWORD_RESET_TOKEN_EXPIRE_MINUTES` | No | Reset-token lifetime |
| `FRONTEND_URL` | Yes for password reset | Reset-link frontend origin |
| `CORS_ORIGINS` | Yes in production | Comma-separated frontend origins |
| `DEFAULT_ADMIN_NAME/USERNAME/EMAIL/PASSWORD` | Local seed only | Configurable default administrator |
| `SMTP_HOST/PORT/USERNAME/PASSWORD/FROM_EMAIL` | Production reset mail | SMTP delivery configuration |
| `OPENAI_API_KEY` | No | Enables external AI insights |
| `AI_MODEL` | No | Configured AI model |

Frontend:

| Variable | Description |
|---|---|
| `VITE_API_URL` | Backend URL ending in `/api`; local default is `/api` through Vite proxy |

Never commit `.env` files or production secrets.

## Migrations and seed data

```powershell
cd backend
alembic upgrade head
python seed_data.py
```

The seed is idempotent and creates one admin and two linked employee accounts. Demo passwords are local-only.

## Demo credentials

| Role | Email | Password |
|---|---|---|
| Admin | `admin@example.com` or `venkatesh` | `Admin@123` |
| Employee | `employee1@globalco.example` | `EmployeeDemo123!` |
| Employee | `employee2@globalco.example` | `EmployeeDemo123!` |

> The default Administrator credentials are intended only for local development. Change the password and configure secure environment variables before deployment.

## Testing and quality

```powershell
cd backend
pytest -q
ruff check app tests seed_data.py

cd ..\frontend
npm run lint
npm run build
```

Tests cover role logins, invalid/inactive login, admin access, employee denial, employee allowed access, AI mocking, and request validation.

## CI/CD

[`.github/workflows/ci.yml`](.github/workflows/ci.yml) runs on every push and pull request. It installs dependencies, lints and tests the backend, validates migrations, lints the frontend, and produces a frontend build. Any failed command fails its job.

## Vercel frontend deployment

1. Import the repository into Vercel.
2. Use the root `vercel.json`.
3. Set `VITE_API_URL=https://<backend-host>/api`.
4. Add the Vercel domain to backend `CORS_ORIGINS`.
5. Deploy. SPA rewrites route browser refreshes to `index.html`.

## Backend deployment

`render.yaml` describes a Render web service. Configure `DATABASE_URL`, `SECRET_KEY`, and `CORS_ORIGINS`; optionally configure the AI variables. The build installs dependencies and runs migrations, and the service starts Uvicorn. See [Deployment](docs/DEPLOYMENT.md).

## API documentation

Interactive OpenAPI is available at `/docs`. The curated endpoint guide is in [API Documentation](docs/API_DOCUMENTATION.md).

## Screenshots

Add final deployment screenshots here before submission:

- Login and role redirect
- Admin dashboard
- Employee dashboard
- Employee management
- Workforce Insights
- Audit logs
- Mobile navigation

## Repository and branch workflow

```bash
git checkout -b feature/globalco-assessment
git add .
git commit -m "feat: add secure RBAC and workforce insights"
git push -u origin feature/globalco-assessment
```

Open a pull request into `main`; GitHub Actions validates the branch and PR.

## Known limitations

- JWTs are bearer tokens stored in browser local storage; production hardening should move them to secure HttpOnly same-site cookies with CSRF protection.
- AI provider calls use a short synchronous timeout and do not currently have queued retries.
- SQLite is intended for local/demo use; production should use managed PostgreSQL.
- Automated frontend component tests are not yet included; lint and production build are enforced.

## Future improvements

- Refresh-token rotation and server-side token revocation
- Fine-grained permission tables beyond the two assessment roles
- Email invitations and administrator-driven forced password rotation
- Scheduled insight reports and trend history
- Playwright end-to-end tests and accessibility audits

## Additional documentation

- [Architecture](docs/ARCHITECTURE.md)
- [API Documentation](docs/API_DOCUMENTATION.md)
- [Deployment](docs/DEPLOYMENT.md)
- [Assessment Summary](docs/ASSESSMENT_SUMMARY.md)
