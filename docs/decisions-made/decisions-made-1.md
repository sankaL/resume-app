# Decisions Made

## 2026-04-07 10:00:16 EDT — Normalize job posting origin on applications

- Status: Accepted
- Context: Application intake previously relied on extracted or manually entered job title, company, and job description, while duplicate review compared only title and company. That left no structured way to record where a posting came from and made duplicate warnings less precise for postings that appear across multiple boards.
- Decision: Add a nullable normalized `job_posting_origin` field to applications, with fixed MVP values for common sources and a conditional free-text companion field when the user selects `Other`. Automatic extraction should classify the origin when confidence is sufficient; otherwise the user can provide or edit it later from manual entry or the application detail page.
- Duplicate-review rule: Consider `job_posting_origin` during duplicate evaluation when both compared applications have it populated, but do not require it. If origin is missing on either side, fall back to the existing title-and-company duplicate check.
- Consequences: The PRD, schema contract, migration runbook, and roadmap now treat posting origin as a first-class application field. Existing rows do not require a backfill and may remain `NULL` until a user or later tooling supplies the value.
