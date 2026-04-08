# PDF Export Service

<cite>
**Referenced Files in This Document**
- [pdf_export.py](file://backend/app/services/pdf_export.py)
- [application_manager.py](file://backend/app/services/application_manager.py)
- [resume_drafts.py](file://backend/app/db/resume_drafts.py)
- [profiles.py](file://backend/app/db/profiles.py)
- [applications.py](file://backend/app/db/applications.py)
- [workflow.py](file://backend/app/services/workflow.py)
- [validation.py](file://agents/validation.py)
- [assembly.py](file://agents/assembly.py)
- [generation.py](file://agents/generation.py)
- [base_resumes.py](file://backend/app/services/base_resumes.py)
- [base_resumes.py (API)](file://backend/app/api/base_resumes.py)
</cite>

## Table of Contents
1. [Introduction](#introduction)
2. [Project Structure](#project-structure)
3. [Core Components](#core-components)
4. [Architecture Overview](#architecture-overview)
5. [Detailed Component Analysis](#detailed-component-analysis)
6. [Dependency Analysis](#dependency-analysis)
7. [Performance Considerations](#performance-considerations)
8. [Troubleshooting Guide](#troubleshooting-guide)
9. [Conclusion](#conclusion)

## Introduction
This document describes the PDF Export Service that generates ATS-compliant resume PDFs from markdown content. It explains the end-to-end pipeline using WeasyPrint, the content transformation process, styling integration, and layout optimization. It also documents integration with resume drafts and generation parameters, quality and compression considerations, and troubleshooting common formatting issues. The service ensures compatibility with Applicant Tracking Systems (ATS) by enforcing strict content and styling rules.

## Project Structure
The PDF export pipeline spans several backend services and agents:
- PDF generation service: transforms markdown to HTML and renders PDF via WeasyPrint.
- Application manager: orchestrates export within the application workflow.
- Data repositories: persist resume drafts and application state.
- Validation agent: enforces ATS safety and content grounding.
- Assembly agent: composes final markdown with personal info and ordered sections.
- Generation agent: produces tailored sections respecting ATS constraints.
- Base resumes service/API: manages user-defined base resumes used as source material.

```mermaid
graph TB
subgraph "Agents"
GEN["Generation Agent<br/>generation.py"]
VAL["Validation Agent<br/>validation.py"]
ASM["Assembly Agent<br/>assembly.py"]
end
subgraph "Backend Services"
AM["Application Manager<br/>application_manager.py"]
PEX["PDF Export Service<br/>pdf_export.py"]
BR_API["Base Resumes API<br/>base_resumes.py (API)"]
BR_SVC["Base Resumes Service<br/>base_resumes.py"]
end
subgraph "Repositories"
RD["Resume Drafts Repo<br/>resume_drafts.py"]
PR["Profiles Repo<br/>profiles.py"]
AR["Applications Repo<br/>applications.py"]
end
subgraph "External"
WP["WeasyPrint"]
end
GEN --> VAL
VAL --> ASM
ASM --> AM
AM --> RD
AM --> PR
AM --> AR
AM --> PEX
PEX --> WP
BR_API --> BR_SVC
BR_SVC --> AM
```

**Diagram sources**
- [pdf_export.py:78-96](file://backend/app/services/pdf_export.py#L78-L96)
- [application_manager.py:1080-1148](file://backend/app/services/application_manager.py#L1080-L1148)
- [resume_drafts.py:14-118](file://backend/app/db/resume_drafts.py#L14-L118)
- [profiles.py:14-68](file://backend/app/db/profiles.py#L14-L68)
- [applications.py:34-60](file://backend/app/db/applications.py#L34-L60)
- [validation.py:231-292](file://agents/validation.py#L231-L292)
- [assembly.py:12-26](file://agents/assembly.py#L12-L26)
- [generation.py:88-112](file://agents/generation.py#L88-L112)
- [base_resumes.py (API): 17-242:17-242](file://backend/app/api/base_resumes.py#L17-L242)
- [base_resumes.py:32-154](file://backend/app/services/base_resumes.py#L32-L154)

**Section sources**
- [pdf_export.py:14-96](file://backend/app/services/pdf_export.py#L14-L96)
- [application_manager.py:1080-1148](file://backend/app/services/application_manager.py#L1080-L1148)
- [resume_drafts.py:14-118](file://backend/app/db/resume_drafts.py#L14-L118)
- [profiles.py:14-68](file://backend/app/db/profiles.py#L14-L68)
- [applications.py:34-60](file://backend/app/db/applications.py#L34-L60)
- [validation.py:231-292](file://agents/validation.py#L231-L292)
- [assembly.py:12-26](file://agents/assembly.py#L12-L26)
- [generation.py:88-112](file://agents/generation.py#L88-L112)
- [base_resumes.py (API): 17-242:17-242](file://backend/app/api/base_resumes.py#L17-L242)
- [base_resumes.py:32-154](file://backend/app/services/base_resumes.py#L32-L154)

## Core Components
- PDF Export Service
  - Converts markdown to an ATS-safe HTML document and renders a PDF using WeasyPrint.
  - Uses a thread pool executor to keep the event loop unblocked and enforces a timeout.
  - Builds a personal header from profile data and applies a fixed, ATS-friendly stylesheet.
- Application Manager
  - Coordinates export within the application workflow, constructs filenames, and updates application state and notifications upon success or failure.
- Resume Drafts Repository
  - Stores markdown content, generation parameters, and timestamps for drafts.
- Profiles Repository
  - Supplies personal info (name, email, phone, address) used in the resume header.
- Applications Repository
  - Tracks application state, failure reasons, and export timestamps.
- Validation Agent
  - Ensures generated content is grounded in the base resume, maintains correct section order, and enforces ATS safety (no tables/images).
- Assembly Agent
  - Composes final markdown with a personal header and ordered sections.
- Generation Agent
  - Produces tailored sections respecting ATS constraints and target page-length guidance.
- Base Resumes Service/API
  - Manages user-defined base resumes used as source material for generation.

**Section sources**
- [pdf_export.py:14-96](file://backend/app/services/pdf_export.py#L14-L96)
- [application_manager.py:1080-1148](file://backend/app/services/application_manager.py#L1080-L1148)
- [resume_drafts.py:14-118](file://backend/app/db/resume_drafts.py#L14-L118)
- [profiles.py:14-68](file://backend/app/db/profiles.py#L14-L68)
- [applications.py:34-60](file://backend/app/db/applications.py#L34-L60)
- [validation.py:231-292](file://agents/validation.py#L231-L292)
- [assembly.py:12-26](file://agents/assembly.py#L12-L26)
- [generation.py:88-112](file://agents/generation.py#L88-L112)
- [base_resumes.py (API): 17-242:17-242](file://backend/app/api/base_resumes.py#L17-L242)
- [base_resumes.py:32-154](file://backend/app/services/base_resumes.py#L32-L154)

## Architecture Overview
The PDF export pipeline integrates generation, validation, assembly, and export orchestration:

```mermaid
sequenceDiagram
participant Client as "Client"
participant AM as "Application Manager"
participant RD as "Resume Drafts Repo"
participant PR as "Profiles Repo"
participant PEX as "PDF Export Service"
participant WP as "WeasyPrint"
Client->>AM : Request export
AM->>RD : Fetch draft (markdown content)
AM->>PR : Fetch profile (personal info)
AM->>PEX : generate_pdf(markdown, personal_info)
PEX->>PEX : Build HTML (ATS-safe CSS)
PEX->>WP : write_pdf()
WP-->>PEX : PDF bytes
PEX-->>AM : PDF bytes
AM->>AM : Update application state and notifications
AM-->>Client : Export result
```

**Diagram sources**
- [application_manager.py:1080-1148](file://backend/app/services/application_manager.py#L1080-L1148)
- [resume_drafts.py:50-60](file://backend/app/db/resume_drafts.py#L50-L60)
- [profiles.py:47-68](file://backend/app/db/profiles.py#L47-L68)
- [pdf_export.py:78-96](file://backend/app/services/pdf_export.py#L78-L96)

## Detailed Component Analysis

### PDF Export Service
- Responsibilities
  - Build an HTML document from markdown with an ATS-safe stylesheet.
  - Optionally include a centered personal header derived from profile data.
  - Render PDF using WeasyPrint in a thread pool executor with a timeout.
- Key behaviors
  - Deferred import of WeasyPrint to avoid module load failures in environments lacking native libraries.
  - Timeout enforcement to prevent long-running conversions.
  - Fixed font family, sizes, and margins optimized for print and ATS parsing.
- Styling integration
  - Serif fonts, modest font sizes, and minimal spacing to reduce layout variance.
  - No tables, images, or decorative elements to maintain ATS compliance.
- Layout optimization
  - Standard heading levels and paragraph spacing improve readability and ATS parsing.
  - Margins configured for standard page layout.

```mermaid
flowchart TD
Start(["Call generate_pdf"]) --> BuildHTML["Build HTML from markdown<br/>+ personal header (optional)"]
BuildHTML --> Render["Render PDF via WeasyPrint<br/>in thread pool executor"]
Render --> Timeout{"Timeout exceeded?"}
Timeout --> |Yes| RaiseTimeout["Raise asyncio.TimeoutError"]
Timeout --> |No| ReturnBytes["Return PDF bytes"]
RaiseTimeout --> End(["Exit"])
ReturnBytes --> End
```

**Diagram sources**
- [pdf_export.py:78-96](file://backend/app/services/pdf_export.py#L78-L96)
- [pdf_export.py:14-68](file://backend/app/services/pdf_export.py#L14-L68)

**Section sources**
- [pdf_export.py:14-96](file://backend/app/services/pdf_export.py#L14-L96)

### Application Manager Export Workflow
- Responsibilities
  - Fetch profile and draft, construct filename, and call the PDF export service.
  - Handle timeouts and exceptions, update application state, and notify users.
- Integration points
  - Reads personal info from profile and markdown content from draft.
  - Updates application exported_at timestamp and internal state on success.
- Notifications and emails
  - Emits success/error notifications and attempts to send an email on failure.

```mermaid
sequenceDiagram
participant AM as "Application Manager"
participant PR as "Profiles Repo"
participant RD as "Resume Drafts Repo"
participant PEX as "PDF Export Service"
participant AR as "Applications Repo"
participant NR as "Notifications Repo"
AM->>PR : fetch_profile(user_id)
PR-->>AM : ProfileRecord
AM->>RD : fetch_draft(user_id, application_id)
RD-->>AM : ResumeDraftRecord
AM->>PEX : generate_pdf(content_md, personal_info)
alt Success
PEX-->>AM : PDF bytes
AM->>AR : update_application(..., exported_at, internal_state)
AM->>NR : create_notification(success)
else Timeout or Error
PEX-->>AM : Exception
AM->>AR : update_application(..., failure_reason)
AM->>NR : create_notification(error)
end
```

**Diagram sources**
- [application_manager.py:1080-1148](file://backend/app/services/application_manager.py#L1080-L1148)
- [profiles.py:47-68](file://backend/app/db/profiles.py#L47-L68)
- [resume_drafts.py:50-60](file://backend/app/db/resume_drafts.py#L50-L60)
- [applications.py:270-308](file://backend/app/db/applications.py#L270-L308)

**Section sources**
- [application_manager.py:1080-1148](file://backend/app/services/application_manager.py#L1080-L1148)
- [applications.py:270-308](file://backend/app/db/applications.py#L270-L308)

### Content Transformation and ATS Safety
- Generation agent
  - Produces sections tailored to a job description while staying grounded in the base resume.
  - Enforces ATS-safe Markdown (no tables/images).
- Validation agent
  - Detects hallucinations by comparing generated content to the base resume.
  - Verifies required sections and correct ordering.
  - Enforces ATS safety rules and auto-applies minor formatting fixes.
- Assembly agent
  - Composes final markdown with a personal header and ordered sections.
  - Ensures personal info comes from the profile, not LLM generation.

```mermaid
flowchart TD
Start(["Start generation"]) --> Gen["Generate sections<br/>generation.py"]
Gen --> Val["Validate content<br/>validation.py"]
Val --> Valid{"Valid?"}
Valid --> |No| FixOrAbort["Report errors and abort"]
Valid --> |Yes| Assemble["Assemble final markdown<br/>assembly.py"]
Assemble --> Export["Export to PDF<br/>pdf_export.py"]
Export --> Done(["Complete"])
```

**Diagram sources**
- [generation.py:88-112](file://agents/generation.py#L88-L112)
- [validation.py:231-292](file://agents/validation.py#L231-L292)
- [assembly.py:12-26](file://agents/assembly.py#L12-L26)
- [pdf_export.py:78-96](file://backend/app/services/pdf_export.py#L78-L96)

**Section sources**
- [generation.py:88-112](file://agents/generation.py#L88-L112)
- [validation.py:231-292](file://agents/validation.py#L231-L292)
- [assembly.py:12-26](file://agents/assembly.py#L12-L26)

### Data Models and Repositories
- ResumeDraftRecord
  - Stores markdown content, generation parameters, sections snapshot, and timestamps.
- ProfileRecord
  - Provides personal info used in the resume header.
- ApplicationRecord
  - Tracks application state, failure reasons, and export timestamps.

```mermaid
erDiagram
RESUME_DRAFTS {
uuid id PK
uuid application_id
uuid user_id
text content_md
jsonb generation_params
jsonb sections_snapshot
timestamptz last_generated_at
timestamptz last_exported_at
timestamptz updated_at
}
PROFILES {
uuid id PK
text email
text name
text phone
text address
uuid default_base_resume_id
jsonb section_preferences
jsonb section_order
timestamptz created_at
timestamptz updated_at
}
APPLICATIONS {
uuid id PK
uuid user_id
text job_url
text job_title
text company
text job_description
uuid base_resume_id
text base_resume_name
text visible_status
text internal_state
text failure_reason
bool applied
float8 duplicate_similarity_score
jsonb duplicate_match_fields
text duplicate_resolution_status
text notes
timestamptz exported_at
timestamptz created_at
timestamptz updated_at
bool has_action_required_notification
}
PROFILES ||--o{ APPLICATIONS : "owns"
PROFILES ||--o{ RESUME_DRAFTS : "owns"
APPLICATIONS ||--o{ RESUME_DRAFTS : "references"
```

**Diagram sources**
- [resume_drafts.py:14-24](file://backend/app/db/resume_drafts.py#L14-L24)
- [profiles.py:14-24](file://backend/app/db/profiles.py#L14-L24)
- [applications.py:34-60](file://backend/app/db/applications.py#L34-L60)

**Section sources**
- [resume_drafts.py:14-118](file://backend/app/db/resume_drafts.py#L14-L118)
- [profiles.py:14-68](file://backend/app/db/profiles.py#L14-L68)
- [applications.py:34-60](file://backend/app/db/applications.py#L34-L60)

### Base Resumes Management
- API endpoints support creating, uploading, listing, updating, deleting, and setting default base resumes.
- Upload endpoint supports optional LLM cleanup of parsed PDF content.
- Service enforces ownership and default resume association.

```mermaid
sequenceDiagram
participant Client as "Client"
participant API as "Base Resumes API"
participant SVC as "Base Resumes Service"
participant Repo as "Base Resume Repo"
participant Prof as "Profile Repo"
Client->>API : POST /upload (PDF)
API->>SVC : create_resume(name, content_md)
SVC->>Repo : create_resume(...)
Repo-->>SVC : Record
SVC-->>API : Detail with is_default flag
API-->>Client : 201 Created
```

**Diagram sources**
- [base_resumes.py (API): 111-169:111-169](file://backend/app/api/base_resumes.py#L111-L169)
- [base_resumes.py:55-73](file://backend/app/services/base_resumes.py#L55-L73)

**Section sources**
- [base_resumes.py (API): 17-242:17-242](file://backend/app/api/base_resumes.py#L17-L242)
- [base_resumes.py:32-154](file://backend/app/services/base_resumes.py#L32-L154)

## Dependency Analysis
- Coupling and cohesion
  - PDF Export Service is cohesive around HTML-to-PDF conversion and has low coupling to external systems.
  - Application Manager orchestrates multiple repositories and services, increasing coupling but centralizing workflow logic.
- External dependencies
  - WeasyPrint is used for PDF rendering; import is deferred to avoid environment-specific failures.
  - Validation agent depends on OpenAI-compatible LLM for structured output.
- Potential circular dependencies
  - No evident circular imports among the analyzed modules.

```mermaid
graph LR
AM["application_manager.py"] --> PEX["pdf_export.py"]
AM --> RD["resume_drafts.py"]
AM --> PR["profiles.py"]
AM --> AR["applications.py"]
PEX --> MD["markdown"]
PEX --> WP["weasyprint"]
VAL["validation.py"] --> LLM["OpenAI-compatible LLM"]
GEN["generation.py"] --> LLM
ASM["assembly.py"] --> AM
```

**Diagram sources**
- [application_manager.py:1080-1148](file://backend/app/services/application_manager.py#L1080-L1148)
- [pdf_export.py:71-75](file://backend/app/services/pdf_export.py#L71-L75)
- [validation.py:89-95](file://agents/validation.py#L89-L95)
- [generation.py:341-348](file://agents/generation.py#L341-L348)

**Section sources**
- [pdf_export.py:71-75](file://backend/app/services/pdf_export.py#L71-L75)
- [application_manager.py:1080-1148](file://backend/app/services/application_manager.py#L1080-L1148)
- [validation.py:89-95](file://agents/validation.py#L89-L95)
- [generation.py:341-348](file://agents/generation.py#L341-L348)

## Performance Considerations
- Concurrency and blocking
  - PDF generation runs in a thread pool executor to avoid blocking the event loop.
  - A timeout is enforced to prevent long-running conversions from stalling the service.
- Rendering cost
  - WeasyPrint rendering cost scales with content length and complexity; prefer ATS-safe, minimal markup.
- File size optimization
  - The current implementation does not apply PDF compression or optimization; consider adding compression options if needed.
- Network latency
  - Validation agent relies on external LLM calls; timeouts and fallback models mitigate latency risks.

[No sources needed since this section provides general guidance]

## Troubleshooting Guide
- PDF export timeout
  - Symptom: asyncio.TimeoutError during export.
  - Resolution: Retry export; ensure content is concise and free of heavy formatting.
  - Related code: timeout enforcement and exception handling.
- Export failure with generic error
  - Symptom: ValueError raised after catching non-timeout exceptions.
  - Resolution: Inspect logs for underlying causes; confirm WeasyPrint availability and environment readiness.
- ATS formatting issues
  - Symptom: ATS parsing problems due to unsupported elements.
  - Resolution: Avoid tables and images; stick to headings, paragraphs, and bullet lists.
- Validation failures
  - Symptom: Validation errors indicating hallucinations, missing sections, wrong order, or ATS violations.
  - Resolution: Regenerate sections to ground claims in the base resume; ensure required sections are present and ordered correctly.
- Filename and state updates
  - Symptom: Application not transitioning to expected state after export.
  - Resolution: Confirm exported_at timestamp and internal_state updates occur on success; verify notifications are created.

**Section sources**
- [application_manager.py:1100-1117](file://backend/app/services/application_manager.py#L1100-L1117)
- [pdf_export.py:11](file://backend/app/services/pdf_export.py#L11)
- [validation.py:231-292](file://agents/validation.py#L231-L292)

## Conclusion
The PDF Export Service provides a robust, ATS-compliant pipeline for generating resumes from markdown content. By combining generation, validation, and assembly with a controlled HTML-to-PDF transformation, it ensures reliable exports suitable for ATS systems. The service’s timeout and asynchronous design help maintain responsiveness, while the repository-driven workflow keeps state consistent across the application lifecycle. For future enhancements, consider adding PDF compression options and expanding styling customization while preserving ATS safety.