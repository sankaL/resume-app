# Database Design

<cite>
**Referenced Files in This Document**
- [20260407_000001_phase_0_foundation.sql](file://supabase/migrations/20260407_000001_phase_0_foundation.sql)
- [20260407_000002_phase_1a_blocked_recovery_extension.sql](file://supabase/migrations/20260407_000002_phase_1a_blocked_recovery_extension.sql)
- [20260407_000003_phase_1a_extracted_reference_id.sql](file://supabase/migrations/20260407_000003_phase_1a_extracted_reference_id.sql)
- [20260407_000004_phase_2_base_resumes.sql](file://supabase/migrations/20260407_000004_phase_2_base_resumes.sql)
- [20260407_000005_phase_3_generation.sql](file://supabase/migrations/20260407_000005_phase_3_generation.sql)
- [00-auth-schema.sql](file://supabase/initdb/00-auth-schema.sql)
- [run_migrations.sh](file://scripts/run_migrations.sh)
- [database_schema.md](file://docs/database_schema.md)
- [backend-database-migration-runbook.md](file://docs/backend-database-migration-runbook.md)
- [docker-compose.yml](file://docker-compose.yml)
- [seed_local_user.sh](file://scripts/seed_local_user.sh)
- [profiles.py](file://backend/app/db/profiles.py)
- [base_resumes.py](file://backend/app/db/base_resumes.py)
- [applications.py](file://backend/app/db/applications.py)
- [resume_drafts.py](file://backend/app/db/resume_drafts.py)
- [notifications.py](file://backend/app/db/notifications.py)
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
10. [Appendices](#appendices)

## Introduction
This document describes the PostgreSQL database design integrated with Supabase for the AI Resume Builder application. It covers the schema, relationships, constraints, migration system, Supabase integration (authentication, authorization, roles, policies), indexing and performance strategies, initialization and seeding, and operational practices for data lifecycle, backups, and disaster recovery. It also provides examples of common queries and data access patterns aligned with the application’s models.

## Project Structure
The database layer is composed of:
- Supabase-managed Postgres with Supabase Auth and PostgREST
- Versioned migrations under supabase/migrations
- Initialization script for the auth schema
- Backend repositories that encapsulate SQL access patterns
- Orchestration via docker-compose and a migration runner

```mermaid
graph TB
subgraph "Supabase Runtime"
DB["PostgreSQL 16"]
AUTH["GoTrue (Auth)"]
REST["PostgREST"]
KONG["Kong Gateway"]
end
subgraph "Dev Orchestration"
DC["docker-compose.yml"]
MR["Migration Runner<br/>run_migrations.sh"]
INIT["initdb/00-auth-schema.sql"]
end
subgraph "Backend"
APP["Backend Services"]
REPO_PROFILES["profiles.py"]
REPO_BASE["base_resumes.py"]
REPO_APPS["applications.py"]
REPO_DRAFT["resume_drafts.py"]
REPO_NOTIF["notifications.py"]
end
DC --> MR
MR --> DB
INIT --> DB
DC --> AUTH
DC --> REST
DC --> KONG
APP --> REPO_PROFILES
APP --> REPO_BASE
APP --> REPO_APPS
APP --> REPO_DRAFT
APP --> REPO_NOTIF
APP --> DB
AUTH --> DB
REST --> DB
KONG --> AUTH
KONG --> REST
```

**Diagram sources**
- [docker-compose.yml:1-191](file://docker-compose.yml#L1-L191)
- [run_migrations.sh:1-39](file://scripts/run_migrations.sh#L1-L39)
- [00-auth-schema.sql:1-2](file://supabase/initdb/00-auth-schema.sql#L1-L2)

**Section sources**
- [docker-compose.yml:1-191](file://docker-compose.yml#L1-L191)
- [run_migrations.sh:1-39](file://scripts/run_migrations.sh#L1-L39)
- [00-auth-schema.sql:1-2](file://supabase/initdb/00-auth-schema.sql#L1-L2)

## Core Components
- Application tables
  - profiles: Application-owned extension of auth.users with preferences and optional extension token fields
  - base_resumes: User-owned Markdown source resumes
  - applications: Job application records with workflow states, duplicate signals, and origin normalization
  - resume_drafts: Single current Markdown draft per application with generation metadata
  - notifications: In-app notifications scoped to users and optionally to applications
- Enums and JSONB contracts are defined in the schema and documented in the schema doc
- Row Level Security (RLS) policies ensure per-user isolation
- Triggers maintain updated_at timestamps
- Indexes optimize common queries (lists, filters, search, notifications)

**Section sources**
- [20260407_000001_phase_0_foundation.sql:86-300](file://supabase/migrations/20260407_000001_phase_0_foundation.sql#L86-L300)
- [database_schema.md:46-230](file://docs/database_schema.md#L46-L230)

## Architecture Overview
The Supabase stack integrates:
- Postgres for persistence
- GoTrue for authentication and JWT issuance
- PostgREST for RESTful API over database views/functions
- Kong as the API gateway and router

```mermaid
graph TB
Client["Browser/App"]
Kong["Kong Gateway"]
Auth["GoTrue (Auth)"]
PostgREST["PostgREST"]
DB["PostgreSQL"]
Client --> Kong
Kong --> Auth
Kong --> PostgREST
PostgREST --> DB
Auth --> DB
```

**Diagram sources**
- [docker-compose.yml:115-186](file://docker-compose.yml#L115-L186)

**Section sources**
- [docker-compose.yml:115-186](file://docker-compose.yml#L115-L186)

## Detailed Component Analysis

### Profiles
- Purpose: Extend auth.users with application-specific fields (preferences, contact info, default resume pointer, optional extension token fields)
- Ownership: One-to-one with auth.users via PK/FK
- RLS: Self-service read/update only for the authenticated user
- Indexes: Unique email, optional unique partial index on extension token hash
- Triggers: updated_at managed automatically

```mermaid
erDiagram
PROFILES {
uuid id PK,FK
text email UK
text name
text phone
text address
uuid default_base_resume_id
jsonb section_preferences
jsonb section_order
text extension_token_hash
timestamptz extension_token_created_at
timestamptz extension_token_last_used_at
timestamptz created_at
timestamptz updated_at
}
BASE_RESUMES {
uuid id PK
uuid user_id FK
text name
text content_md
timestamptz created_at
timestamptz updated_at
}
PROFILES }o--|| BASE_RESUMES : "default_base_resume_id -> id where user_id=id"
```

**Diagram sources**
- [20260407_000001_phase_0_foundation.sql:86-118](file://supabase/migrations/20260407_000001_phase_0_foundation.sql#L86-L118)

**Section sources**
- [20260407_000001_phase_0_foundation.sql:86-118](file://supabase/migrations/20260407_000001_phase_0_foundation.sql#L86-L118)
- [database_schema.md:48-83](file://docs/database_schema.md#L48-L83)

### Base Resumes
- Purpose: Store user-owned Markdown source resumes
- Ownership: Scoped by user_id
- Constraints: Non-empty name/content; composite unique with user_id
- RLS: Owner-only operations
- Indexes: List by updated_at desc, name lookup, standalone user_id index added in phase 2

```mermaid
erDiagram
BASE_RESUMES {
uuid id PK
uuid user_id FK
text name
text content_md
timestamptz created_at
timestamptz updated_at
}
PROFILES {
uuid id PK,FK
uuid default_base_resume_id FK
}
BASE_RESUMES }o--|| PROFILES : "referenced by default_base_resume_id"
```

**Diagram sources**
- [20260407_000001_phase_0_foundation.sql:99-109](file://supabase/migrations/20260407_000001_phase_0_foundation.sql#L99-L109)
- [20260407_000001_phase_0_foundation.sql:111-118](file://supabase/migrations/20260407_000001_phase_0_foundation.sql#L111-L118)

**Section sources**
- [20260407_000001_phase_0_foundation.sql:99-118](file://supabase/migrations/20260407_000001_phase_0_foundation.sql#L99-L118)
- [20260407_000004_phase_2_base_resumes.sql:14-76](file://supabase/migrations/20260407_000004_phase_2_base_resumes.sql#L14-L76)
- [database_schema.md:84-113](file://docs/database_schema.md#L84-L113)

### Applications
- Purpose: Track job applications, workflow state, duplicate signals, origin normalization, and failure details
- Ownership: Scoped by user_id
- Constraints: Non-empty job_url; bounds for duplicate similarity; conditional validations for origin ‘other’
- RLS: Owner-only operations
- Indexes: Lists by updated_at desc, status-filtered lists, search GIN trigram, unresolved duplicate attention, extracted reference ID lookup

```mermaid
erDiagram
APPLICATIONS {
uuid id PK
uuid user_id FK
text job_url
text job_title
text company
text job_description
text extracted_reference_id
enum job_posting_origin
text job_posting_origin_other_text
uuid base_resume_id FK
enum visible_status
enum internal_state
enum failure_reason
jsonb extraction_failure_details
jsonb generation_failure_details
boolean applied
numeric duplicate_similarity_score
jsonb duplicate_match_fields
enum duplicate_resolution_status
uuid duplicate_matched_application_id FK
text notes
timestamptz exported_at
timestamptz created_at
timestamptz updated_at
}
APPLICATIONS ||--o{ APPLICATIONS : "duplicate_matched_application_id self-ref"
APPLICATIONS }o--|| BASE_RESUMES : "base_resume_id"
```

**Diagram sources**
- [20260407_000001_phase_0_foundation.sql:120-174](file://supabase/migrations/20260407_000001_phase_0_foundation.sql#L120-L174)
- [20260407_000003_phase_1a_extracted_reference_id.sql:3-8](file://supabase/migrations/20260407_000003_phase_1a_extracted_reference_id.sql#L3-L8)

**Section sources**
- [20260407_000001_phase_0_foundation.sql:120-174](file://supabase/migrations/20260407_000001_phase_0_foundation.sql#L120-L174)
- [20260407_000002_phase_1a_blocked_recovery_extension.sql:12-13](file://supabase/migrations/20260407_000002_phase_1a_blocked_recovery_extension.sql#L12-L13)
- [20260407_000005_phase_3_generation.sql:7-8](file://supabase/migrations/20260407_000005_phase_3_generation.sql#L7-L8)
- [database_schema.md:114-168](file://docs/database_schema.md#L114-L168)

### Resume Drafts
- Purpose: Store the single current Markdown draft per application with generation parameters and sections snapshot
- Ownership: Scoped by user_id; cascade delete with application
- Constraints: Non-empty content; unique per application
- RLS: Owner-only operations
- Indexes: Unique index on application_id

```mermaid
erDiagram
RESUME_DRAFTS {
uuid id PK
uuid application_id FK,UK
uuid user_id FK
text content_md
jsonb generation_params
jsonb sections_snapshot
timestamptz last_generated_at
timestamptz last_exported_at
timestamptz updated_at
}
APPLICATIONS {
uuid id PK
}
RESUME_DRAFTS }o--|| APPLICATIONS : "application_id"
```

**Diagram sources**
- [20260407_000001_phase_0_foundation.sql:176-197](file://supabase/migrations/20260407_000001_phase_0_foundation.sql#L176-L197)

**Section sources**
- [20260407_000001_phase_0_foundation.sql:176-197](file://supabase/migrations/20260407_000001_phase_0_foundation.sql#L176-L197)
- [database_schema.md:169-200](file://docs/database_schema.md#L169-L200)

### Notifications
- Purpose: In-app notifications scoped to users and optionally to applications
- Ownership: Scoped by user_id
- Constraints: Non-empty message; optional application linkage
- RLS: Owner-only operations
- Indexes: Inbox queries by read and created_at; unread action-required attention

```mermaid
erDiagram
NOTIFICATIONS {
uuid id PK
uuid user_id FK
uuid application_id FK
enum type
text message
boolean action_required
boolean read
timestamptz created_at
}
APPLICATIONS {
uuid id PK
}
NOTIFICATIONS }o--|| APPLICATIONS : "application_id"
```

**Diagram sources**
- [20260407_000001_phase_0_foundation.sql:199-218](file://supabase/migrations/20260407_000001_phase_0_foundation.sql#L199-L218)

**Section sources**
- [20260407_000001_phase_0_foundation.sql:199-218](file://supabase/migrations/20260407_000001_phase_0_foundation.sql#L199-L218)
- [database_schema.md:201-230](file://docs/database_schema.md#L201-L230)

### Migration System
- Versioning: Migrations are named with a timestamp prefix and applied in order
- Metadata: app_meta.schema_migrations tracks applied versions
- Runner: Iterates through files, checks applied versions, applies SQL, and records completion
- Phases:
  - Phase 0: Foundation (tables, enums, triggers, RLS, indexes, auth profile sync)
  - Phase 1A: Blocked recovery and extension token fields
  - Phase 1A: Extracted reference ID for duplicate detection
  - Phase 2: Granular RLS policies and base_resumes user_id index
  - Phase 3: Generation failure details

```mermaid
flowchart TD
Start(["Start Migration Runner"]) --> EnsureMeta["Ensure app_meta.schema_migrations exists"]
EnsureMeta --> ListFiles["List sorted SQL files"]
ListFiles --> ForEach["For each file"]
ForEach --> CheckApplied{"Already applied?"}
CheckApplied --> |Yes| Skip["Skip file"]
CheckApplied --> |No| Apply["Apply SQL file"]
Apply --> Record["Insert version into schema_migrations"]
Record --> Next["Next file"]
Skip --> Next
Next --> Done(["Done"])
```

**Diagram sources**
- [run_migrations.sh:18-38](file://scripts/run_migrations.sh#L18-L38)

**Section sources**
- [run_migrations.sh:1-39](file://scripts/run_migrations.sh#L1-L39)
- [20260407_000001_phase_0_foundation.sql:1-343](file://supabase/migrations/20260407_000001_phase_0_foundation.sql#L1-L343)
- [20260407_000002_phase_1a_blocked_recovery_extension.sql:1-16](file://supabase/migrations/20260407_000002_phase_1a_blocked_recovery_extension.sql#L1-L16)
- [20260407_000003_phase_1a_extracted_reference_id.sql:1-11](file://supabase/migrations/20260407_000003_phase_1a_extracted_reference_id.sql#L1-L11)
- [20260407_000004_phase_2_base_resumes.sql:1-158](file://supabase/migrations/20260407_000004_phase_2_base_resumes.sql#L1-L158)
- [20260407_000005_phase_3_generation.sql:1-11](file://supabase/migrations/20260407_000005_phase_3_generation.sql#L1-L11)

### Supabase Integration
- Roles and Policies
  - Roles: anon, authenticated, service_role
  - Policies: per-table, per-operation policies enforcing ownership
- Authentication
  - Auth schema initialization
  - Service role JWT audience and admin roles configured
- Authorization
  - RLS enabled on all user-scoped tables
  - Policies restrict to auth.uid() = owner key
- Database Configuration
  - PostgREST configured with JWT secret and app settings
  - Kong configured with Supabase keys and plugins

```mermaid
sequenceDiagram
participant Client as "Client"
participant Kong as "Kong"
participant Auth as "GoTrue"
participant PGRST as "PostgREST"
participant DB as "PostgreSQL"
Client->>Kong : Request with Authorization header
Kong->>Auth : Validate JWT (JWKS)
Auth-->>Kong : JWT claims (aud=authenticated, sub=user_id)
Kong->>PGRST : Forward request (with JWT)
PGRST->>DB : Execute query with RLS
DB-->>PGRST : Results filtered by RLS
PGRST-->>Client : Response
```

**Diagram sources**
- [docker-compose.yml:115-186](file://docker-compose.yml#L115-L186)

**Section sources**
- [20260407_000001_phase_0_foundation.sql:254-340](file://supabase/migrations/20260407_000001_phase_0_foundation.sql#L254-L340)
- [00-auth-schema.sql:1-2](file://supabase/initdb/00-auth-schema.sql#L1-L2)
- [docker-compose.yml:115-186](file://docker-compose.yml#L115-L186)

### Indexing Strategies and Performance
- Profiles: unique email; optional unique partial index on extension token hash
- Base Resumes: composite indexes for list/search; standalone user_id index
- Applications: list ordering, status filter, unresolved duplicates, GIN trigram search, extracted reference ID index
- Resume Drafts: unique index per application
- Notifications: inbox sort and unread/action-required attention index
- Triggers: set_updated_at on all tables

```mermaid
flowchart TD
QStart(["Query Pattern"]) --> ListApps["List applications by user"]
ListApps --> UseIndex["Use (user_id, updated_at desc)"]
QStart --> FilterByStatus["Filter by visible_status"]
FilterByStatus --> UseIndex2["Use (user_id, visible_status, updated_at desc)"]
QStart --> SearchApps["Search job_title/company"]
SearchApps --> UseGIN["Use GIN trigram index"]
QStart --> UnreadAction["Unread action-required notifications"]
UnreadAction --> UsePartial["Use partial index (action_required=true, read=false)"]
QStart --> DraftLookup["Per-application draft lookup"]
DraftLookup --> UseUnique["Use unique index (application_id)"]
```

**Diagram sources**
- [20260407_000001_phase_0_foundation.sql:220-232](file://supabase/migrations/20260407_000001_phase_0_foundation.sql#L220-L232)
- [20260407_000004_phase_2_base_resumes.sql:155-155](file://supabase/migrations/20260407_000004_phase_2_base_resumes.sql#L155-L155)

**Section sources**
- [20260407_000001_phase_0_foundation.sql:220-232](file://supabase/migrations/20260407_000001_phase_0_foundation.sql#L220-L232)
- [20260407_000004_phase_2_base_resumes.sql:147-155](file://supabase/migrations/20260407_000004_phase_2_base_resumes.sql#L147-L155)
- [database_schema.md:248-265](file://docs/database_schema.md#L248-L265)

### Database Initialization and Access Control Setup
- Initialization
  - Auth schema created in initdb
  - Migrations applied by migration-runner container after DB and Auth are healthy
- Access control
  - Roles granted usage on schema and table/sequence privileges to authenticated/service_role
  - RLS enabled on all user-scoped tables
  - Per-operation policies for base_resumes and resume_drafts refined in phase 2

```mermaid
sequenceDiagram
participant DC as "docker-compose"
participant DB as "PostgreSQL"
participant MR as "Migration Runner"
participant AUTH as "GoTrue"
participant META as "app_meta.schema_migrations"
DC->>DB : Start DB (initdb mounted)
DB-->>DC : Healthy
DC->>AUTH : Start Auth
AUTH-->>DC : Healthy
DC->>MR : Run migrations
MR->>DB : Create app_meta and table
MR->>DB : Apply each SQL migration
MR->>META : Insert version
MR-->>DC : Completed
```

**Diagram sources**
- [docker-compose.yml:85-114](file://docker-compose.yml#L85-L114)
- [run_migrations.sh:18-38](file://scripts/run_migrations.sh#L18-L38)
- [00-auth-schema.sql:1-2](file://supabase/initdb/00-auth-schema.sql#L1-L2)

**Section sources**
- [docker-compose.yml:85-114](file://docker-compose.yml#L85-L114)
- [run_migrations.sh:18-38](file://scripts/run_migrations.sh#L18-L38)
- [00-auth-schema.sql:1-2](file://supabase/initdb/00-auth-schema.sql#L1-L2)

### Data Lifecycle Management, Backup, and Disaster Recovery
- Lifecycle
  - Additive-first migrations to preserve backward compatibility
  - Backfills in bounded batches when needed
  - Clear failure details on recoverable success
- Backup
  - Use Postgres native logical or physical backups
  - Schedule regular snapshots of supabase-db-data volume
- Disaster Recovery
  - Restore from latest backup to a new DB container
  - Re-run migrations via migration-runner
  - Recreate Kong/Auth/PostgREST if needed

[No sources needed since this section provides general guidance]

### Examples of Common Queries and Data Access Patterns
- Backend repositories encapsulate SQL and return Pydantic models
- Typical operations:
  - Fetch profile by user_id
  - Upsert extension token and rotate tokens
  - List base resumes by user_id ordered by updated_at desc
  - Create application and return hydrated record with base resume name and action-required flag
  - Upsert resume draft with ON CONFLICT handling
  - Create notification and clear action-required flags

```mermaid
sequenceDiagram
participant Repo as "Repository"
participant DB as "PostgreSQL"
Repo->>DB : SELECT ... FROM profiles WHERE id = ?
DB-->>Repo : Row
Repo-->>Repo : Model validation
Repo-->>Caller : ProfileRecord
```

**Diagram sources**
- [profiles.py:47-68](file://backend/app/db/profiles.py#L47-L68)

**Section sources**
- [profiles.py:47-68](file://backend/app/db/profiles.py#L47-L68)
- [base_resumes.py:40-57](file://backend/app/db/base_resumes.py#L40-L57)
- [applications.py:132-160](file://backend/app/db/applications.py#L132-L160)
- [resume_drafts.py:62-118](file://backend/app/db/resume_drafts.py#L62-L118)
- [notifications.py:31-57](file://backend/app/db/notifications.py#L31-L57)

## Dependency Analysis
- Backend repositories depend on the database schema and RLS policies
- Supabase runtime (Auth, PostgREST, Kong) depends on database availability and proper configuration
- Migrations define schema contracts and must be applied before backend code that relies on new shapes

```mermaid
graph LR
AUTH["GoTrue"] --> DB["PostgreSQL"]
PGRST["PostgREST"] --> DB
KONG["Kong"] --> AUTH
KONG --> PGRST
APP["Backend Repositories"] --> DB
MIG["Migrations"] --> DB
MIG -.-> APP
```

**Diagram sources**
- [docker-compose.yml:115-186](file://docker-compose.yml#L115-L186)

**Section sources**
- [docker-compose.yml:115-186](file://docker-compose.yml#L115-L186)

## Performance Considerations
- Prefer composite indexes that match common ORDER BY and WHERE clauses
- Use GIN trigram indexes for text search within user scope
- Keep JSONB shapes validated to avoid expensive parsing overhead
- Use ON CONFLICT WHERE for upserts that must respect ownership
- Maintain updated_at via triggers to support consistent list ordering

[No sources needed since this section provides general guidance]

## Troubleshooting Guide
- Migration issues
  - Verify app_meta.schema_migrations table exists and is populated
  - Check migration-runner logs for SQL errors
  - Ensure DB and Auth are healthy before running migrations
- Auth and RLS
  - Confirm JWT audience and service role configuration
  - Validate RLS policies are present and using auth.uid()
- Seed user
  - Use seed script with SERVICE_ROLE_KEY to create invited users
  - Ensure gateway health before attempting admin user creation

**Section sources**
- [run_migrations.sh:18-38](file://scripts/run_migrations.sh#L18-L38)
- [seed_local_user.sh:29-60](file://scripts/seed_local_user.sh#L29-L60)
- [docker-compose.yml:115-186](file://docker-compose.yml#L115-L186)

## Conclusion
The database design centers on strict per-user ownership with RLS, additive migrations, and pragmatic indexing to support dashboard and workflow operations. Supabase Auth and PostgREST provide secure, standards-based access, while the migration runner ensures deterministic schema evolution. The backend repositories translate application needs into efficient SQL, maintaining data integrity and performance.

[No sources needed since this section summarizes without analyzing specific files]

## Appendices

### Appendix A: Migration Runbook Highlights
- Define schema changes in the schema doc first
- Prefer additive changes; stage destructive changes carefully
- Add RLS, indexes, and constraints in the same migration
- Backfill in batches; keep readers defensive
- Verify auth, ownership, and status alignment post-deploy

**Section sources**
- [backend-database-migration-runbook.md:18-63](file://docs/backend-database-migration-runbook.md#L18-L63)

### Appendix B: Supabase Roles and Permissions Summary
- Roles: anon, authenticated, service_role
- Privileges: schema usage; table/sequence access for authenticated/service_role
- Policies: per-table, per-operation ownership enforcement

**Section sources**
- [20260407_000001_phase_0_foundation.sql:254-256](file://supabase/migrations/20260407_000001_phase_0_foundation.sql#L254-L256)
- [20260407_000001_phase_0_foundation.sql:302-340](file://supabase/migrations/20260407_000001_phase_0_foundation.sql#L302-L340)