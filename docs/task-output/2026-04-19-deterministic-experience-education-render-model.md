# 2026-04-19 — Deterministic Experience and Education Render Model

## Summary

Implemented a shared resume render/parser pipeline so `Professional Experience` and `Education` normalize into one canonical two-row contract and render consistently in the generated preview, PDF export, and DOCX export.

## What Changed

- Added backend resume render service at `backend/app/services/resume_render.py`.
- Normalized generated, regenerated, manually saved, and exported drafts through the same canonicalizer.
- Extended draft API responses with:
  - `render_contract_version`
  - `render_model`
  - `render_error`
- Switched the generated draft preview to use the semantic render model when available.
- Updated PDF and DOCX export to render structured experience and education rows with shared left/right alignment semantics.
- Standardized the canonical row order:
  - Experience row 1: `company | location`
  - Experience row 2: `role title | date range`
  - Education row 1: `school | location`
  - Education row 2: `degree/program | graduation date`
- Increased export readability by separating section headings from body content more clearly and giving structured headers stronger hierarchy than bullet text.

## Validation And Safety

- Legacy parseable drafts are rewritten into canonical Markdown on save.
- Malformed structured experience or education blocks fail closed instead of being stored with drifting layout.
- Export now uses the same normalized content path as preview, reducing PDF/DOCX divergence.

## Verification

- `PYTHONPATH=backend python3 -m pytest backend/tests/test_pdf_export.py -q`
- `PYTHONPATH=agents python3 -m pytest agents/tests/test_experience_contract.py agents/tests/test_generation_pipeline.py -q`
- `PYTHONPATH=backend python3 -m pytest backend/tests/test_phase1_applications.py -q -k "save_draft_edit_normalizes_legacy_experience_and_education_blocks or save_draft_edit_rejects_malformed_structured_experience_blocks"`
- `cd frontend && npm test -- --run src/test/resume-render-preview.test.tsx src/test/markdown-preview.test.tsx`
