export const jobPostingOriginOptions = [
  { value: "linkedin", label: "LinkedIn" },
  { value: "indeed", label: "Indeed" },
  { value: "google_jobs", label: "Google Jobs" },
  { value: "glassdoor", label: "Glassdoor" },
  { value: "ziprecruiter", label: "ZipRecruiter" },
  { value: "monster", label: "Monster" },
  { value: "dice", label: "Dice" },
  { value: "company_website", label: "Company Website" },
  { value: "other", label: "Other" },
] as const;

export const visibleStatusLabels = {
  draft: "Draft",
  needs_action: "Needs Action",
  in_progress: "In Progress",
  complete: "Complete",
} as const;

export const PAGE_LENGTH_OPTIONS = [
  { value: "1_page", label: "1 Page", description: "Target 450-700 words with an 850-word hard cap." },
  { value: "2_page", label: "2 Pages", description: "Target 900-1400 words with a 1600-word hard cap." },
  { value: "3_page", label: "3 Pages", description: "Target 1500-2100 words with a 2400-word hard cap." },
] as const;

export const AGGRESSIVENESS_OPTIONS = [
  {
    value: "low",
    label: "Low",
    description: "Light edits to Summary and Experience only. Skills stay as-is. Education is never rewritten.",
  },
  {
    value: "medium",
    label: "Medium",
    description: "Rewrite Summary, reorder Experience, and regroup or prune Skills. Education stays fixed.",
  },
  {
    value: "high",
    label: "High",
    description: "Most assertive rewrite for Summary, Experience, and Skills while staying source-grounded. Education stays fixed.",
  },
] as const;
