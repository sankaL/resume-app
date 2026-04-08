BEGIN;

-- ============================================================================
-- Phase 3: Generation support — add generation_failure_details to applications
-- ============================================================================

ALTER TABLE public.applications
  ADD COLUMN IF NOT EXISTS generation_failure_details jsonb;

COMMIT;
