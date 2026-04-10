# Task Output — Railway Selective Main Deploy Automation

**Date:** 2026-04-10 17:00:08 EDT  
**Scope:** Connect `main` branch pushes to Railway deployments and ensure only changed services redeploy.

## Summary

- Created and linked Railway project `job-app-prod` for this repo.
- Added Railway services `backend` and `frontend`.
- Added GitHub Actions workflow `.github/workflows/deploy-railway-main.yml` for path-filtered selective deploys on `push` to `main`.
- Configured repository secrets for Railway deploy targeting and authentication.

## Delivered Outcomes

- Railway project:
  - Project ID: `ae2da7e0-d415-41dc-8682-0365ff2cb0f7`
  - Environment: `production` (`6247a7ab-26b0-44ac-be1a-dbf9ba5dd4dc`)
- Railway services:
  - `backend` (`4b9900dd-8fbf-4d33-a817-d58c2b2c46ec`)
  - `frontend` (`6e69181c-b625-4c85-85d9-b60e7bf8b3e2`)
- GitHub Actions deploy flow:
  - Detects changed paths using `dorny/paths-filter`.
  - Deploys `backend` only when backend/shared/infra paths change.
  - Deploys `frontend` only when frontend/shared/infra paths change.
  - Uses `railway up <path> --path-as-root` with explicit project/service targeting.
- GitHub repository secrets configured:
  - `RAILWAY_TOKEN`
  - `RAILWAY_PROJECT_ID`
  - `RAILWAY_BACKEND_SERVICE_ID`
  - `RAILWAY_FRONTEND_SERVICE_ID`

## Verification

- Verified Railway project/service IDs through `railway status --json`.
- Verified GitHub secrets existence with `gh secret list --repo sankaL/resume-app`.
- Workflow syntax and path conditions reviewed locally; first live execution will occur on next push to `main`.
