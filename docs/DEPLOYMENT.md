# Deployment

## Frontend on Vercel

1. Import the Git repository.
2. Keep the project root at repository root; `vercel.json` runs the frontend build.
3. Set `VITE_API_URL` to the public backend URL plus `/api`.
4. Deploy and copy the resulting HTTPS origin.
5. Add that exact origin to backend `CORS_ORIGINS`.

The SPA rewrite supports direct loading of `/admin/dashboard` and `/employee/dashboard`.

## Backend on Render

1. Create a Blueprint using `render.yaml`, or create a Python web service with root directory `backend`.
2. Build: `pip install -r requirements.txt`
3. Start: `sh start.sh`. This runs `alembic upgrade head` before Uvicorn.
4. Configure:
   - `DATABASE_URL`: managed PostgreSQL URL
   - `SECRET_KEY`: long random secret
   - `CORS_ORIGINS`: Vercel production origin
   - `ACCESS_TOKEN_EXPIRE_MINUTES`
   - optional `OPENAI_API_KEY` and `AI_MODEL`
   - `FRONTEND_URL` and SMTP variables for production password-reset email
5. Never run `python seed_data.py` in production. The script now refuses to run
   when `ENVIRONMENT=production`. Create the first administrator through a
   controlled one-time process and use unique credentials.
6. Run the read-only admin and employee smoke checks described below.

Production mode deliberately refuses to start unless PostgreSQL, a unique
32+ character secret, exact HTTPS CORS/frontend origins, and complete SMTP
credentials are configured.

## Post-deployment smoke test

Run from `backend` with dedicated test accounts:

```bash
SMOKE_API_URL=https://your-api.example.com \
SMOKE_ADMIN_IDENTIFIER=deployment-admin@example.com \
SMOKE_ADMIN_PASSWORD='unique-password' \
SMOKE_EMPLOYEE_IDENTIFIER=deployment-employee@example.com \
SMOKE_EMPLOYEE_PASSWORD='unique-password' \
python scripts/smoke_test.py
```

The script performs only GET requests after login and verifies authentication,
dashboards, employees, departments, attendance, payroll, and leave access.

## Optional OpenAI verification

Set `ENABLE_EXTERNAL_AI=true`, `OPENAI_API_KEY`, and `AI_MODEL`, then run:

```bash
python -m scripts.verify_openai
```

This uses synthetic aggregate metrics and fails if the call falls back to the
local rules engine.

## Production checklist

- Replace demo passwords and do not seed public production environments.
- Use PostgreSQL, HTTPS, managed secrets, backups, and restricted CORS.
- Enable automated daily PostgreSQL backups and point-in-time recovery in the
  database provider; periodically test a restore into a temporary database.
- Monitor `/health/ready` with the hosting provider or an uptime monitor and
  configure alerts for failures, high latency, HTTP 5xx responses, and database
  storage. Retain Render application logs for the assessment period.
- Keep the application rate limiter enabled and add edge/gateway rate limiting
  in Cloudflare or the chosen API gateway for distributed enforcement.
- Move bearer tokens to HttpOnly secure cookies before handling sensitive production data.
- Monitor server logs without recording tokens, passwords, or private employee fields.
