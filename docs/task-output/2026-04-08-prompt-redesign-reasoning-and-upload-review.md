# 2026-04-08 — Prompt Redesign, Generation Reasoning, and Upload Review Warnings

## Summary

Implemented a prompt and generation overhaul across the agents, backend, and frontend:

- Replaced the resume-generation prompt with an expert resume-writer contract that includes section rules, section-specific aggressiveness behavior, word-budget guidance, and a no-em-dash rule.
- Enabled OpenRouter reasoning only for resume-generation calls, with medium reasoning for initial full generation and high reasoning for full or section regeneration.
- Switched generation to prefer structured output while preserving a strict prompt-level JSON fallback on the same model before moving to the configured fallback model.
- Added deterministic screening for unsafe user instructions that try to override constraints or inject new facts.
- Added other-section context to section regeneration so regenerated sections stay more coherent with the rest of the draft.
- Hardened extraction prompt instructions and made upload cleanup return a review warning when the parsed resume still looks unreliable.

## Files Changed

- `agents/generation.py`
- `agents/validation.py`
- `agents/worker.py`
- `backend/app/api/applications.py`
- `backend/app/api/base_resumes.py`
- `backend/app/services/resume_parser.py`
- `frontend/src/lib/api.ts`
- `frontend/src/lib/application-options.ts`
- `frontend/src/routes/ApplicationDetailPage.tsx`
- `frontend/src/routes/BaseResumeEditorPage.tsx`
- `docs/prompts.md`

## Verification

- `python3 -m pytest agents/tests/test_generation_pipeline.py -q`
- `python3 -m pytest backend/tests/test_resume_parser.py backend/tests/test_application_request_validation.py -q`
- `npm run build` in `frontend/`

## Notes

- `python3 -m pytest agents/tests/test_worker.py -q` could not run in this environment because `playwright` is not installed, so worker-level extraction tests remain unverified here.
