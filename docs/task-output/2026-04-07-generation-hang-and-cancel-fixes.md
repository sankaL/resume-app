# Task Output — Generation Hang and Cancel Fixes

**Date:** 2026-04-07 22:45:00 EDT  
**Scope:** Fix stuck generation UX, align worker and backend callback contracts, make cancel and timeout recovery schema-safe, and add regression coverage.

## Summary

- Fixed generation and regeneration worker callbacks so they now send the nested `generated` and `failure` payloads the backend already expects.
- Stopped treating every `generation_pending` application as an actively running workflow. Active initial generation now enters `generating`, while `generation_pending` is reserved for ready or retryable initial-generation states.
- Added schema support for `generation_timeout` and `generation_cancelled`, plus terminal progress job-id fencing so late worker callbacks cannot overwrite cancelled or timed-out rows.
- Updated the application detail page to poll immediately for active generation, stop polling on terminal progress, and render retry or failure UI instead of a misleading progress card for failed `generation_pending` rows.

## Delivered Outcomes

- Current failed applications with `internal_state = generation_pending` and `failure_reason = generation_failed` no longer present as stuck active jobs in the UI.
- `/api/applications/:id/cancel-generation` now returns a recoverable conflict for non-active rows instead of a schema-driven `500`.
- Successful generation callbacks now persist drafts and transition to `resume_ready` instead of collapsing into generic failures because of malformed callback payloads.
- Timeout and cancel recovery paths now remain compatible with the shared workflow contract, the database enum, and the frontend failure UI.

## Verification Added

- Backend service tests for generation success persistence, rejecting cancel on failed retryable rows, ignoring stale callbacks after cancel, and timeout recovery.
- Worker tests for nested success and failure callback payload shapes.
- Frontend tests for immediate active-generation polling and for rendering failed `generation_pending` rows as retryable failures instead of active generation.
