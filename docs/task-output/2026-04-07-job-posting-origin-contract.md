# Task Output — Job Posting Origin Contract Update

**Date:** 2026-04-07 10:00:16 EDT
**Scope:** Add job posting origin as a documented application field across intake, duplicate review, and schema planning.

## Summary

- Added `job_posting_origin` to the product contract as a normalized field that should be extracted automatically when possible.
- Added manual support for the same field during extraction fallback and later application-detail edits, with a conditional free-text label when the user selects `Other`.
- Updated duplicate-review requirements so origin contributes to duplicate evaluation when present, without blocking duplicate checks when origin is unknown.

## Documents Updated

- `docs/resume_builder_PRD_v3.md`
- `docs/database_schema.md`
- `docs/backend-database-migration-runbook.md`
- `docs/build-plan.md`
- `docs/decisions-made/decisions-made-1.md`

## Implementation Notes

- MVP normalized options are LinkedIn, Indeed, Google Jobs, Glassdoor, ZipRecruiter, Monster, Dice, Company Website, and Other.
- Existing application rows can keep `NULL` origin values until a user or future tooling supplies them.
- Duplicate warnings should include `job_posting_origin` in `matched_fields` only when it was actually part of the comparison.
