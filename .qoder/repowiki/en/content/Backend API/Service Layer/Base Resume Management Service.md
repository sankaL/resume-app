# Base Resume Management Service

<cite>
**Referenced Files in This Document**
- [backend/app/api/base_resumes.py](file://backend/app/api/base_resumes.py)
- [backend/app/services/base_resumes.py](file://backend/app/services/base_resumes.py)
- [backend/app/db/base_resumes.py](file://backend/app/db/base_resumes.py)
- [backend/app/db/profiles.py](file://backend/app/db/profiles.py)
- [backend/app/services/resume_parser.py](file://backend/app/services/resume_parser.py)
- [backend/app/api/applications.py](file://backend/app/api/applications.py)
- [backend/app/db/applications.py](file://backend/app/db/applications.py)
- [backend/app/services/application_manager.py](file://backend/app/services/application_manager.py)
- [frontend/src/routes/BaseResumesPage.tsx](file://frontend/src/routes/BaseResumesPage.tsx)
- [frontend/src/routes/BaseResumeEditorPage.tsx](file://frontend/src/routes/BaseResumeEditorPage.tsx)
- [frontend/src/lib/api.ts](file://frontend/src/lib/api.ts)
- [supabase/migrations/20260407_000004_phase_2_base_resumes.sql](file://supabase/migrations/20260407_000004_phase_2_base_resumes.sql)
- [docs/database_schema.md](file://docs/database_schema.md)
- [backend/tests/test_base_resume_service.py](file://backend/tests/test_base_resume_service.py)
</cite>

## Update Summary
**Changes Made**
- Enhanced deletion safety mechanisms with improved exception handling for database constraints
- Added comprehensive test coverage for deletion scenarios including referenced resumes and foreign key violations
- Improved error mapping for better user feedback during deletion operations
- Strengthened database constraint handling with proper cleanup of related references

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
10. [Appendices](#appendices)

## Introduction
This document describes the Base Resume Management Service that powers user-managed resume templates and content. It covers the service architecture for creating, updating, retrieving, and deleting base resumes, along with integration points to application workflows. The system stores resume content as Markdown, supports PDF uploads with optional AI cleanup, and integrates with profile data to inject personal information and section preferences during generation.

**Updated** Enhanced with improved deletion safety mechanisms, comprehensive exception handling for database constraints, and extensive test coverage for deletion scenarios.

## Project Structure
The Base Resume Management Service spans backend APIs, services, repositories, and frontend UI components:

- Backend API layer exposes endpoints for base resume CRUD and default selection
- Service layer encapsulates business logic and validation with enhanced error handling
- Repository layer handles database operations with PostgreSQL and RLS, including automatic cleanup of related references
- Frontend pages provide user interfaces for creating, editing, uploading, and setting default base resumes
- Database schema defines tables, constraints, enums, and RLS policies with proper cascade handling

```mermaid
graph TB
subgraph "Frontend"
BRP["BaseResumesPage.tsx"]
BRE["BaseResumeEditorPage.tsx"]
API["frontend/src/lib/api.ts"]
end
subgraph "Backend"
APIBR["backend/app/api/base_resumes.py"]
SBR["backend/app/services/base_resumes.py"]
RBR["backend/app/db/base_resumes.py"]
RP["backend/app/db/profiles.py"]
RPR["backend/app/services/resume_parser.py"]
APIAPP["backend/app/api/applications.py"]
RAPP["backend/app/db/applications.py"]
SAPP["backend/app/services/application_manager.py"]
end
subgraph "Database"
BR_TABLE["base_resumes"]
P_TABLE["profiles"]
APP_TABLE["applications"]
end
BRP --> API
BRE --> API
API --> APIBR
APIBR --> SBR
SBR --> RBR
SBR --> RP
APIBR --> RPR
APIAPP --> SAPP
SAPP --> RAPP
SAPP --> RBR
SAPP --> RP
RBR --> BR_TABLE
RP --> P_TABLE
RAPP --> APP_TABLE
```

**Diagram sources**
- [backend/app/api/base_resumes.py:1-256](file://backend/app/api/base_resumes.py#L1-L256)
- [backend/app/services/base_resumes.py:1-163](file://backend/app/services/base_resumes.py#L1-L163)
- [backend/app/db/base_resumes.py:1-196](file://backend/app/db/base_resumes.py#L1-L196)
- [backend/app/db/profiles.py:1-225](file://backend/app/db/profiles.py#L1-L225)
- [backend/app/services/resume_parser.py:1-228](file://backend/app/services/resume_parser.py#L1-L228)
- [backend/app/api/applications.py:1-661](file://backend/app/api/applications.py#L1-L661)
- [backend/app/db/applications.py:1-328](file://backend/app/db/applications.py#L1-L328)
- [backend/app/services/application_manager.py:1-800](file://backend/app/services/application_manager.py#L1-L800)
- [frontend/src/routes/BaseResumesPage.tsx:1-185](file://frontend/src/routes/BaseResumesPage.tsx#L1-L185)
- [frontend/src/routes/BaseResumeEditorPage.tsx:1-472](file://frontend/src/routes/BaseResumeEditorPage.tsx#L1-L472)
- [frontend/src/lib/api.ts:1-489](file://frontend/src/lib/api.ts#L1-L489)

**Section sources**
- [backend/app/api/base_resumes.py:1-256](file://backend/app/api/base_resumes.py#L1-L256)
- [backend/app/services/base_resumes.py:1-163](file://backend/app/services/base_resumes.py#L1-L163)
- [backend/app/db/base_resumes.py:1-196](file://backend/app/db/base_resumes.py#L1-L196)
- [backend/app/db/profiles.py:1-225](file://backend/app/db/profiles.py#L1-L225)
- [backend/app/services/resume_parser.py:1-228](file://backend/app/services/resume_parser.py#L1-L228)
- [backend/app/api/applications.py:1-661](file://backend/app/api/applications.py#L1-L661)
- [backend/app/db/applications.py:1-328](file://backend/app/db/applications.py#L1-L328)
- [backend/app/services/application_manager.py:1-800](file://backend/app/services/application_manager.py#L1-L800)
- [frontend/src/routes/BaseResumesPage.tsx:1-185](file://frontend/src/routes/BaseResumesPage.tsx#L1-L185)
- [frontend/src/routes/BaseResumeEditorPage.tsx:1-472](file://frontend/src/routes/BaseResumeEditorPage.tsx#L1-L472)
- [frontend/src/lib/api.ts:1-489](file://frontend/src/lib/api.ts#L1-L489)

## Core Components
- Base Resume API: Provides endpoints for listing, creating, uploading, retrieving, updating, deleting, and setting default base resumes
- Base Resume Service: Implements validation, ownership checks, default flag computation, and enhanced deletion semantics with comprehensive error handling
- Base Resume Repository: Handles database operations with PostgreSQL and RLS enforcement, including automatic cleanup of related references
- Profile Repository: Manages user profile defaults and section preferences used during generation
- Resume Parser Service: Extracts and optionally cleans up PDF content into Markdown
- Application Integration: Links base resumes to applications and injects profile data and preferences during generation

Key responsibilities:
- Content management: Store and manage Markdown-based resume content
- Ownership and permissions: Enforce user scoping via RLS and explicit user_id checks
- Default selection: Normalize default base resume selection into profile-level pointer
- Generation integration: Supply personal info and section preferences to generation pipeline
- **Enhanced Deletion Safety**: Prevent deletion conflicts with applications, handle database constraint violations, and provide clear error feedback

**Updated** Enhanced deletion safety with improved exception handling for database constraints and comprehensive test coverage.

**Section sources**
- [backend/app/api/base_resumes.py:85-256](file://backend/app/api/base_resumes.py#L85-L256)
- [backend/app/services/base_resumes.py:32-163](file://backend/app/services/base_resumes.py#L32-L163)
- [backend/app/db/base_resumes.py:31-196](file://backend/app/db/base_resumes.py#L31-L196)
- [backend/app/db/profiles.py:38-225](file://backend/app/db/profiles.py#L38-L225)
- [backend/app/services/resume_parser.py:13-228](file://backend/app/services/resume_parser.py#L13-L228)
- [backend/app/api/applications.py:560-580](file://backend/app/api/applications.py#L560-L580)
- [backend/app/db/applications.py:123-328](file://backend/app/db/applications.py#L123-L328)
- [backend/app/services/application_manager.py:513-602](file://backend/app/services/application_manager.py#L513-L602)

## Architecture Overview
The Base Resume Management Service follows a layered architecture:
- Presentation: FastAPI endpoints define the contract and handle request validation
- Service: Encapsulates business rules, validation, and cross-entity logic with enhanced error handling
- Persistence: PostgreSQL with Row Level Security (RLS) policies and explicit user_id scoping
- Integration: Applications reference base resumes and generation consumes profile data and preferences

```mermaid
sequenceDiagram
participant FE as "Frontend"
participant API as "Base Resume API"
participant SVC as "Base Resume Service"
participant REP as "Base Resume Repository"
participant DB as "PostgreSQL"
FE->>API : "POST /api/base-resumes"
API->>SVC : "create_resume(user_id, name, content_md)"
SVC->>REP : "create_resume(user_id, name, content_md)"
REP->>DB : "INSERT INTO base_resumes"
DB-->>REP : "Record"
REP-->>SVC : "Record"
SVC-->>API : "ResumeDetailWithDefaultFlag"
API-->>FE : "201 Created + BaseResumeDetail"
```

**Diagram sources**
- [backend/app/api/base_resumes.py:97-112](file://backend/app/api/base_resumes.py#L97-L112)
- [backend/app/services/base_resumes.py:56-74](file://backend/app/services/base_resumes.py#L56-L74)
- [backend/app/db/base_resumes.py:59-90](file://backend/app/db/base_resumes.py#L59-L90)

**Section sources**
- [backend/app/api/base_resumes.py:1-256](file://backend/app/api/base_resumes.py#L1-L256)
- [backend/app/services/base_resumes.py:1-163](file://backend/app/services/base_resumes.py#L1-L163)
- [backend/app/db/base_resumes.py:1-196](file://backend/app/db/base_resumes.py#L1-L196)

## Detailed Component Analysis

### Base Resume API Layer
Endpoints:
- GET /api/base-resumes: List summaries with default flag
- POST /api/base-resumes: Create a new base resume
- POST /api/base-resumes/upload: Upload PDF, parse to Markdown, optionally clean with LLM, then create
- GET /api/base-resumes/{resume_id}: Retrieve detailed resume
- PATCH /api/base-resumes/{resume_id}: Partially update name/content
- DELETE /api/base-resumes/{resume_id}: Delete with optional force flag and enhanced error handling
- POST /api/base-resumes/{resume_id}/set-default: Set as default via profile pointer

Validation:
- Name must be non-blank for create/update
- PDF upload validates extension, content type, and size
- LLM cleanup is optional and gracefully falls back if API key is missing

Error mapping:
- Translates service exceptions to appropriate HTTP status codes with enhanced error handling
- **Improved Error Mapping**: Better distinction between different types of deletion failures

**Updated** Enhanced error mapping for better user feedback during deletion operations.

**Section sources**
- [backend/app/api/base_resumes.py:85-256](file://backend/app/api/base_resumes.py#L85-L256)

### Base Resume Service Layer
Responsibilities:
- Ownership verification: Fetches records to confirm ownership before updates/deletes
- Validation: Ensures non-blank names and strips whitespace
- Default flag: Computes whether a resume is the user's default by checking profile pointer
- **Enhanced Deletion Semantics**: Prevents deletion if referenced by applications unless force=true, with comprehensive error handling

Integration:
- Uses ProfileRepository to compute default flag and update default pointer
- Uses BaseResumeRepository for persistence operations with automatic cleanup

**Updated** Enhanced with improved deletion safety mechanisms and comprehensive exception handling.

**Section sources**
- [backend/app/services/base_resumes.py:32-163](file://backend/app/services/base_resumes.py#L32-L163)

### Base Resume Repository Layer
Operations:
- list_resumes(user_id): Returns summaries ordered by updated_at desc
- create_resume(user_id, name, content_md): Inserts and returns created record
- fetch_resume(user_id, resume_id): Retrieves a single resume
- update_resume(resume_id, user_id, updates): Updates selected fields with dynamic assignment
- **Enhanced delete_resume**: Deletes with automatic cleanup of related references and proper error handling
- is_referenced(user_id, resume_id): Checks if resume is referenced by applications

**Enhanced Operations**:
- Automatic cleanup: Clears profile default pointers and application references before deletion
- Cascade handling: Properly handles database constraints and foreign key relationships
- Error propagation: Raises appropriate exceptions for constraint violations

SQL patterns:
- Dynamic SQL construction for selective updates
- Composite foreign key constraints enforced via application joins
- **Automatic Cleanup**: Ensures related records are properly cleaned up during deletion

**Updated** Enhanced with automatic cleanup of related references and improved constraint handling.

**Section sources**
- [backend/app/db/base_resumes.py:31-196](file://backend/app/db/base_resumes.py#L31-L196)

### Profile Integration and Default Selection
- Default base resume is stored in profiles.default_base_resume_id
- Setting default updates profile pointer; service computes is_default flag
- During generation, application manager reads profile personal info and section preferences to assemble the resume

**Section sources**
- [backend/app/db/profiles.py:196-221](file://backend/app/db/profiles.py#L196-L221)
- [backend/app/services/base_resumes.py:42-44](file://backend/app/services/base_resumes.py#L42-L44)
- [backend/app/services/application_manager.py:542-556](file://backend/app/services/application_manager.py#L542-L556)

### PDF Upload and Parsing Pipeline
- Validates file type (.pdf), content type, and size (≤10MB)
- Parses PDF to Markdown using ResumeParserService
- Optional LLM cleanup via OpenRouter API if configured
- Creates base resume with parsed/cleaned content

```mermaid
sequenceDiagram
participant FE as "Frontend"
participant API as "Base Resume API"
participant PARSER as "ResumeParserService"
participant SVC as "Base Resume Service"
participant REP as "Base Resume Repository"
FE->>API : "POST /api/base-resumes/upload (multipart)"
API->>PARSER : "parse_pdf(file_bytes)"
alt "use_llm_cleanup"
API->>PARSER : "cleanup_with_llm(raw_markdown)"
end
API->>SVC : "create_resume(user_id, name, content_md)"
SVC->>REP : "create_resume(...)"
REP-->>SVC : "Record"
SVC-->>API : "BaseResumeDetail"
API-->>FE : "201 Created"
```

**Diagram sources**
- [backend/app/api/base_resumes.py:114-182](file://backend/app/api/base_resumes.py#L114-L182)
- [backend/app/services/resume_parser.py:24-228](file://backend/app/services/resume_parser.py#L24-L228)
- [backend/app/services/base_resumes.py:56-74](file://backend/app/services/base_resumes.py#L56-L74)
- [backend/app/db/base_resumes.py:59-90](file://backend/app/db/base_resumes.py#L59-L90)

**Section sources**
- [backend/app/api/base_resumes.py:114-182](file://backend/app/api/base_resumes.py#L114-L182)
- [backend/app/services/resume_parser.py:13-228](file://backend/app/services/resume_parser.py#L13-L228)

### Application Workflow Integration
- Applications can link to a base resume via base_resume_id with ON DELETE SET NULL constraint
- During generation, the application manager injects profile personal info and section preferences
- The linked base resume content serves as the Markdown template for assembly

```mermaid
sequenceDiagram
participant APPAPI as "Applications API"
participant APPSVC as "ApplicationService"
participant BRREP as "BaseResumeRepository"
participant PROF as "ProfileRepository"
APPAPI->>APPSVC : "trigger_generation(user_id, application_id, base_resume_id, ...)"
APPSVC->>BRREP : "fetch_resume(user_id, base_resume_id)"
BRREP-->>APPSVC : "BaseResumeRecord"
APPSVC->>PROF : "fetch_profile(user_id)"
PROF-->>APPSVC : "ProfileRecord"
APPSVC->>APPSVC : "Inject personal_info + section_preferences"
APPSVC-->>APPAPI : "Queued generation"
```

**Diagram sources**
- [backend/app/api/applications.py:560-580](file://backend/app/api/applications.py#L560-L580)
- [backend/app/services/application_manager.py:513-602](file://backend/app/services/application_manager.py#L513-L602)
- [backend/app/db/applications.py:123-328](file://backend/app/db/applications.py#L123-L328)
- [backend/app/db/base_resumes.py:92-109](file://backend/app/db/base_resumes.py#L92-L109)
- [backend/app/db/profiles.py:47-68](file://backend/app/db/profiles.py#L47-L68)

**Section sources**
- [backend/app/api/applications.py:560-580](file://backend/app/api/applications.py#L560-L580)
- [backend/app/services/application_manager.py:513-602](file://backend/app/services/application_manager.py#L513-L602)
- [backend/app/db/applications.py:123-328](file://backend/app/db/applications.py#L123-L328)

### Frontend Integration
- BaseResumesPage displays list of base resumes with default badge and actions
- BaseResumeEditorPage supports three modes:
  - Blank creation: Start from scratch with Markdown editor
  - Upload: Select PDF, review extracted content, then save
  - Edit: Update existing resume name/content
- API helpers wrap authenticated requests for base resume operations

**Section sources**
- [frontend/src/routes/BaseResumesPage.tsx:12-185](file://frontend/src/routes/BaseResumesPage.tsx#L12-L185)
- [frontend/src/routes/BaseResumeEditorPage.tsx:19-472](file://frontend/src/routes/BaseResumeEditorPage.tsx#L19-L472)
- [frontend/src/lib/api.ts:328-397](file://frontend/src/lib/api.ts#L328-L397)

### Enhanced Deletion Safety and Exception Handling
**New Section** - Comprehensive deletion safety mechanisms with improved error handling

The Base Resume Management Service now includes enhanced deletion safety with comprehensive exception handling:

#### Deletion Flow with Enhanced Safety
1. **Ownership Verification**: Confirms user owns the resume before deletion
2. **Reference Checking**: Verifies if resume is referenced by applications
3. **Force Parameter Handling**: Allows deletion with force=true for referenced resumes
4. **Database Constraint Handling**: Properly handles foreign key violations
5. **Automatic Cleanup**: Clears related references before deletion

#### Exception Handling Improvements
- **LookupError**: Raised when resume not found
- **PermissionError**: Raised for constraint violations during deletion
- **ValueError**: Raised for validation failures (e.g., referenced resume without force)
- **psycopg.errors.ForeignKeyViolation**: Properly mapped to PermissionError

#### Test Coverage Enhancements
Comprehensive test coverage ensures reliable deletion behavior:
- Blocks deletion of referenced resumes without force parameter
- Allows deletion of referenced resumes with force=true
- Handles missing records appropriately
- Maps database constraint violations to meaningful errors

**Section sources**
- [backend/app/services/base_resumes.py:109-137](file://backend/app/services/base_resumes.py#L109-L137)
- [backend/app/db/base_resumes.py:153-177](file://backend/app/db/base_resumes.py#L153-L177)
- [backend/tests/test_base_resume_service.py:57-105](file://backend/tests/test_base_resume_service.py#L57-L105)

## Dependency Analysis
- API depends on Service for business logic with enhanced error handling
- Service depends on Repositories for persistence with automatic cleanup
- Repositories depend on PostgreSQL with RLS policies and proper constraint handling
- Applications depend on Base Resume and Profile repositories for generation
- Frontend depends on API for all operations

```mermaid
graph LR
APIBR["base_resumes.py"] --> SBR["services/base_resumes.py"]
SBR --> RBR["db/base_resumes.py"]
SBR --> RP["db/profiles.py"]
APIAPP["api/applications.py"] --> SAPP["services/application_manager.py"]
SAPP --> RAPP["db/applications.py"]
SAPP --> RBR
SAPP --> RP
FE["frontend"] --> APIBR
FE --> APIAPP
```

**Diagram sources**
- [backend/app/api/base_resumes.py:1-256](file://backend/app/api/base_resumes.py#L1-L256)
- [backend/app/services/base_resumes.py:1-163](file://backend/app/services/base_resumes.py#L1-L163)
- [backend/app/db/base_resumes.py:1-196](file://backend/app/db/base_resumes.py#L1-L196)
- [backend/app/db/profiles.py:1-225](file://backend/app/db/profiles.py#L1-L225)
- [backend/app/api/applications.py:1-661](file://backend/app/api/applications.py#L1-L661)
- [backend/app/services/application_manager.py:1-800](file://backend/app/services/application_manager.py#L1-L800)
- [frontend/src/lib/api.ts:1-489](file://frontend/src/lib/api.ts#L1-L489)

**Section sources**
- [backend/app/api/base_resumes.py:1-256](file://backend/app/api/base_resumes.py#L1-L256)
- [backend/app/services/base_resumes.py:1-163](file://backend/app/services/base_resumes.py#L1-L163)
- [backend/app/db/base_resumes.py:1-196](file://backend/app/db/base_resumes.py#L1-L196)
- [backend/app/db/profiles.py:1-225](file://backend/app/db/profiles.py#L1-L225)
- [backend/app/api/applications.py:1-661](file://backend/app/api/applications.py#L1-L661)
- [backend/app/services/application_manager.py:1-800](file://backend/app/services/application_manager.py#L1-L800)
- [frontend/src/lib/api.ts:1-489](file://frontend/src/lib/api.ts#L1-L489)

## Performance Considerations
- Database indexing: Composite indexes on base_resumes(user_id, updated_at DESC) and applications(user_id, updated_at DESC) optimize list queries
- RLS overhead: Policies are efficient due to indexes on user_id; ensure queries filter by user_id
- PDF parsing: Async LLM cleanup is optional; without API key, parsing falls back to basic extraction
- Frontend caching: Consider memoizing base resume lists and details to reduce network calls
- **Enhanced Deletion Performance**: Automatic cleanup reduces orphaned records and improves database performance

**Updated** Enhanced deletion performance with automatic cleanup of related references.

## Troubleshooting Guide
Common issues and resolutions:
- 400 Bad Request
  - Blank name validation failures during create/update
  - Invalid PDF file type or size exceeded
- 404 Not Found
  - Resume not found due to wrong user_id or missing record
  - Profile not found when generating
- **Enhanced Conflict Handling**
  - **409 Conflict**: Attempted deletion of a resume referenced by applications without force=true
  - **PermissionError**: Database constraint violations during deletion attempts
- 500 Internal Server Error
  - Unexpected server errors mapped from service exceptions

Operational tips:
- Verify user_id scoping in all requests
- Ensure profile has required fields (name, email, phone, address) before generation
- Confirm section_preferences and section_order are valid JSONB shapes
- **Deletion Best Practices**: Use force=true only when you understand the implications for referenced applications

**Updated** Enhanced conflict handling and improved error messaging for deletion operations.

**Section sources**
- [backend/app/api/base_resumes.py:75-85](file://backend/app/api/base_resumes.py#L75-L85)
- [backend/app/services/base_resumes.py:128-137](file://backend/app/services/base_resumes.py#L128-L137)
- [backend/app/db/profiles.py:158-188](file://backend/app/db/profiles.py#L158-L188)

## Conclusion
The Base Resume Management Service provides a robust, user-scoped system for managing Markdown-based resume templates. It integrates seamlessly with application workflows by linking base resumes to job applications and injecting profile data and section preferences during generation. Strong validation, RLS policies, and clear CRUD operations ensure data integrity and user autonomy.

**Updated** Enhanced with improved deletion safety mechanisms, comprehensive exception handling for database constraints, and extensive test coverage ensuring reliable and predictable behavior for all deletion scenarios.

## Appendices

### Database Schema Highlights
- base_resumes: Stores user-owned Markdown resumes with non-blank constraints and proper cascade handling
- profiles: Contains default_base_resume_id and section preferences/order
- applications: Links to base_resumes via base_resume_id with ON DELETE SET NULL constraint

**Section sources**
- [docs/database_schema.md:93-122](file://docs/database_schema.md#L93-L122)
- [docs/database_schema.md:123-140](file://docs/database_schema.md#L123-L140)
- [docs/database_schema.md:48-77](file://docs/database_schema.md#L48-L77)

### RLS Policy Summary
- base_resumes: SELECT/INSERT/UPDATE/DELETE allowed only when auth.uid() = user_id
- profiles: SELECT/INSERT/UPDATE allowed only when auth.uid() = id
- applications: SELECT/INSERT/UPDATE/DELETE allowed only when auth.uid() = user_id

**Section sources**
- [supabase/migrations/20260407_000004_phase_2_base_resumes.sql:14-73](file://supabase/migrations/20260407_000004_phase_2_base_resumes.sql#L14-L73)
- [docs/database_schema.md:266-281](file://docs/database_schema.md#L266-L281)

### Enhanced Deletion Safety Features
**New Section** - Technical details of enhanced deletion safety mechanisms

#### Automatic Reference Cleanup
The Base Resume Repository automatically handles cleanup of related references during deletion:

1. **Profile Default Pointer Cleanup**: Updates profiles.default_base_resume_id to null when a resume is deleted
2. **Application Reference Cleanup**: Sets applications.base_resume_id to null for all applications referencing the deleted resume
3. **Cascade Handling**: Properly handles database constraints and foreign key relationships

#### Exception Handling Hierarchy
Proper exception mapping ensures meaningful error messages:

- **LookupError**: "Base resume not found." - Raised when attempting to delete non-existent records
- **ValueError**: "This resume is referenced by one or more applications. Use force=true to delete anyway." - Raised for referenced resumes without force parameter
- **PermissionError**: "This resume cannot be deleted because related records still reference it." - Raised for database constraint violations
- **psycopg.errors.ForeignKeyViolation**: Mapped to PermissionError for constraint violations

#### Test Coverage Summary
Comprehensive test coverage ensures reliability:

- **Deletion Blocking**: Tests prevent deletion of referenced resumes without force parameter
- **Force Deletion**: Tests allow deletion of referenced resumes with force=true
- **Missing Records**: Tests handle attempts to delete non-existent records
- **Constraint Violations**: Tests verify proper mapping of database constraint violations

**Section sources**
- [backend/app/db/base_resumes.py:153-177](file://backend/app/db/base_resumes.py#L153-L177)
- [backend/app/services/base_resumes.py:128-137](file://backend/app/services/base_resumes.py#L128-L137)
- [backend/tests/test_base_resume_service.py:57-105](file://backend/tests/test_base_resume_service.py#L57-L105)