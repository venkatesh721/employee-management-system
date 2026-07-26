# Security

- bcrypt password hashing and expiring signed JWT access tokens
- generic forgot-password response and single-use, expiring reset tokens
- backend RBAC dependencies plus employee row ownership checks
- employee attendance/payroll writes denied regardless of UI
- unique database constraints protect employee links, attendance dates, and payroll months
- audit records for sensitive administrative changes
- environment-controlled CORS and secrets
- policy upload allow-list, UTF-8 sanitization, and 2 MB limit
- safe, predefined HR analytics queries; no generated SQL

Production should terminate TLS at the hosting provider, use PostgreSQL backups, rotate secrets, configure SMTP, and place endpoint rate limiting at the gateway. The current app performs a one-minute forgot-password throttle; a distributed rate limiter is recommended for multi-instance deployments.
