# AI and decision-support features

Attendance risk uses a transparent 30-day weighted score for absences, late arrivals, and half days. Attendance and payroll anomaly alerts use explainable thresholds. Results include a score, factors, expected range, model version, and a human-review notice.

The admin HR assistant maps supported natural-language patterns to predefined aggregate functions. It cannot execute SQL. Unsupported questions return `422`.

The policy assistant chunks sanitized UTF-8 `.txt`/`.md` files and performs deterministic keyword retrieval. Answers cite document and section. When no evidence matches, it explicitly reports that the information is unavailable.

External AI is off by default (`ENABLE_EXTERNAL_AI=false`). The existing workforce insight service falls back safely to deterministic rules. Passwords, tokens, full payroll records, and unrelated personal data are never sent to a provider.

Limitations: rules are decision support, not disciplinary decisions; keyword retrieval is less semantic than embeddings; attendance risk quality depends on sufficient history; all alerts require human review.
