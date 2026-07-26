# Database schema

The schema is managed by Alembic. UUID primary keys are used throughout.

| Area | Tables | Critical constraints |
|---|---|---|
| Identity | `users`, `employees`, `departments` | unique email/username; exactly one employee per `user_id` |
| Attendance | `attendance`, `audit_logs` | unique employee/date; creator/updater metadata |
| Payroll | `salary_structures`, `payroll_records`, `payroll_audit_logs` | unique employee/month; `NUMERIC(12,2)` money |
| Leave | `leave_requests`, `leave_balances` | unique employee/leave type balance; overlap checked in service |
| Decision support | `ai_insights`, `ai_anomalies` | model version, score, explanation, generation time |
| Policy retrieval | `policy_documents`, `policy_document_chunks` | source document and section retained for citations |

Employee-facing queries always derive `employee_id` from the authenticated `user_id`; client-supplied ownership identifiers are ignored or rejected.

Migration `20260726_03` repairs old accounts by first linking a matching unlinked profile by email. Only when no match exists does it create one profile, then it adds uniqueness constraints without deleting data.
