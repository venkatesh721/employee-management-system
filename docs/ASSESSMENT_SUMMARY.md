# GLOBALCO Assessment Summary

## AI-defined business value

Workforce Insights converts employee/attendance aggregates into actionable admin recommendations. It supports an external AI provider, validates input and structured output, excludes personal data, handles provider failures, and includes a practical deterministic fallback.

## Full-stack application

React/Vite provides responsive role-aware dashboards and workflows. FastAPI/SQLAlchemy provides validated APIs, JWT authentication, RBAC, scoped data access, migrations, and audit logging.

## Role-based security

Admin-only APIs use `require_admin`; employee attendance uses server-derived ownership. Frontend route guards and navigation match backend permissions. Invalid tokens return 401, role violations return 403, and inactive users cannot log in.

## Git repository

`.gitignore` excludes dependencies, virtual environments, builds, databases, coverage, logs, and secrets. Environment examples contain names and safe defaults only.

## CI/CD

`.github/workflows/ci.yml` runs backend Ruff, migrations, pytest, frontend ESLint, and the Vite production build for pushes and pull requests. Failures are not suppressed.

## Testing

Backend tests cover:

- successful admin and employee login
- invalid and inactive login
- admin API access
- employee rejection from admin APIs
- employee allowed API access
- mocked AI success
- insight validation and role denial

Frontend lint and production build provide static and bundling verification.

## Deployment

`vercel.json` supports frontend Vercel builds and SPA routes. `render.yaml` describes backend deployment, migration, start, health check, and required environment configuration.

## Documentation

The README covers business context, setup, roles, architecture, database, auth, testing, CI, deployment, credentials, limitations, and improvements. Dedicated API, architecture, deployment, and assessment documents provide evaluator-focused detail.
