# Configuration and Environment

<cite>
**Referenced Files in This Document**
- [backend/app/core/config.py](file://backend/app/core/config.py)
- [backend/app/core/auth.py](file://backend/app/core/auth.py)
- [backend/app/core/security.py](file://backend/app/core/security.py)
- [backend/app/main.py](file://backend/app/main.py)
- [backend/app/api/session.py](file://backend/app/api/session.py)
- [frontend/src/lib/env.ts](file://frontend/src/lib/env.ts)
- [frontend/src/lib/supabase.ts](file://frontend/src/lib/supabase.ts)
- [frontend/src/routes/ProtectedRoute.tsx](file://frontend/src/routes/ProtectedRoute.tsx)
- [frontend/src/lib/api.ts](file://frontend/src/lib/api.ts)
- [frontend/public/chrome-extension/manifest.json](file://frontend/public/chrome-extension/manifest.json)
- [frontend/public/chrome-extension/popup.js](file://frontend/public/chrome-extension/popup.js)
- [docker-compose.yml](file://docker-compose.yml)
- [backend/Dockerfile](file://backend/Dockerfile)
- [agents/Dockerfile](file://agents/Dockerfile)
- [agents/pyproject.toml](file://agents/pyproject.toml)
- [backend/pyproject.toml](file://backend/pyproject.toml)
- [frontend/package.json](file://frontend/package.json)
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
This document provides comprehensive configuration and environment documentation for the multi-component system. It covers:
- Environment configuration management, including settings management, environment variables, configuration validation, and secret management strategies
- Authentication integration with Supabase, including JWT configuration, session management, and role-based access control
- Security configuration including CORS policies, CSRF protection, and API security measures
- Frontend environment configuration including API endpoint configuration, feature flags, and development vs production settings
- Integration between frontend, backend, and AI agent components
- Best practices for environment setup, configuration validation, and security hardening
- Examples of common configuration scenarios and troubleshooting configuration issues

## Project Structure
The system comprises three primary components:
- Backend (FastAPI): Provides APIs, authentication verification, CORS configuration, and worker callback security
- Frontend (React/Vite): Manages environment variables, Supabase session handling, protected routing, and API requests
- Agents (Python/ARQ): Performs extraction and generation tasks, integrates with backend via callbacks and secrets

```mermaid
graph TB
subgraph "Frontend"
FE_Env["Environment Validation<br/>frontend/src/lib/env.ts"]
FE_Supa["Supabase Client<br/>frontend/src/lib/supabase.ts"]
FE_Route["Protected Route<br/>frontend/src/routes/ProtectedRoute.tsx"]
FE_API["API Client<br/>frontend/src/lib/api.ts"]
FE_Ext["Chrome Extension<br/>frontend/public/chrome-extension/*"]
end
subgraph "Backend"
BE_Main["FastAPI App & CORS<br/>backend/app/main.py"]
BE_Config["Settings & Validation<br/>backend/app/core/config.py"]
BE_Auth["JWT Verifier<br/>backend/app/core/auth.py"]
BE_Sec["Worker Secret & Extension Token<br/>backend/app/core/security.py"]
BE_Session["Session Bootstrap<br/>backend/app/api/session.py"]
end
subgraph "Agents"
AG_Worker["Worker Settings & Jobs<br/>agents/worker.py"]
AG_Docker["Agents Dockerfile<br/>agents/Dockerfile"]
end
subgraph "Compose"
DC["docker-compose.yml"]
BE_Docker["Backend Dockerfile<br/>backend/Dockerfile"]
end
FE_Env --> FE_Supa
FE_Supa --> FE_API
FE_Route --> FE_API
FE_API --> BE_Main
FE_Ext --> FE_API
BE_Main --> BE_Auth
BE_Main --> BE_Sec
BE_Auth --> BE_Session
BE_Sec --> AG_Worker
DC --> FE_Env
DC --> BE_Config
DC --> AG_Worker
BE_Docker --> BE_Main
AG_Docker --> AG_Worker
```

**Diagram sources**
- [frontend/src/lib/env.ts:1-15](file://frontend/src/lib/env.ts#L1-L15)
- [frontend/src/lib/supabase.ts:1-26](file://frontend/src/lib/supabase.ts#L1-L26)
- [frontend/src/routes/ProtectedRoute.tsx:1-44](file://frontend/src/routes/ProtectedRoute.tsx#L1-L44)
- [frontend/src/lib/api.ts:177-214](file://frontend/src/lib/api.ts#L177-L214)
- [frontend/public/chrome-extension/popup.js:109-135](file://frontend/public/chrome-extension/popup.js#L109-L135)
- [backend/app/main.py:14-22](file://backend/app/main.py#L14-L22)
- [backend/app/core/config.py:35-96](file://backend/app/core/config.py#L35-L96)
- [backend/app/core/auth.py:22-69](file://backend/app/core/auth.py#L22-L69)
- [backend/app/core/security.py:13-54](file://backend/app/core/security.py#L13-L54)
- [backend/app/api/session.py:27-44](file://backend/app/api/session.py#L27-L44)
- [agents/worker.py:290-305](file://agents/worker.py#L290-L305)
- [docker-compose.yml:1-191](file://docker-compose.yml#L1-L191)
- [backend/Dockerfile:1-18](file://backend/Dockerfile#L1-L18)
- [agents/Dockerfile:1-14](file://agents/Dockerfile#L1-L14)

**Section sources**
- [docker-compose.yml:1-191](file://docker-compose.yml#L1-L191)
- [backend/app/core/config.py:35-96](file://backend/app/core/config.py#L35-L96)
- [frontend/src/lib/env.ts:1-15](file://frontend/src/lib/env.ts#L1-L15)

## Core Components
This section documents environment configuration management, validation, and secret handling across components.

- Backend Settings and Validation
  - Centralized settings model defines environment variables for app environment, dev mode, API port, app URL, database URL, Redis URL, CORS origins, Supabase URLs, JWT configuration, worker callback secret, duplicate similarity threshold, email notifications, shared contract path, and OpenRouter configuration.
  - Email settings are validated to ensure required keys are present when notifications are enabled.
  - CORS origins are parsed into a list for middleware configuration.
  - Settings are cached via a factory function for reuse.

- Frontend Environment Validation
  - Zod schema enforces presence and shape of environment variables for app environment, dev mode, Supabase URL, Supabase anonymous key, and API URL.
  - Parsing occurs at module initialization, ensuring early failures if variables are missing or invalid.

- Agent Settings and Secrets
  - Worker settings include app environment, dev mode, Redis URL, backend API URL, worker callback secret, shared contract path, OpenRouter configuration, and model names for extraction, generation, and validation.
  - Worker callback requires a shared secret header for backend callbacks.
  - OpenRouter API key and model names are validated to be present before use.

- Secret Management Strategies
  - Backend verifies worker callbacks using a shared secret header.
  - Extension-to-backend communication uses a hashed token stored in the database and verified via a dedicated endpoint.
  - Supabase JWT verification supports JWK-based verification and falls back to a shared secret when configured.

**Section sources**
- [backend/app/core/config.py:35-96](file://backend/app/core/config.py#L35-L96)
- [frontend/src/lib/env.ts:1-15](file://frontend/src/lib/env.ts#L1-L15)
- [agents/worker.py:54-71](file://agents/worker.py#L54-L71)
- [backend/app/core/security.py:13-54](file://backend/app/core/security.py#L13-L54)

## Architecture Overview
The system integrates frontend, backend, and agents through environment-driven configuration and secure communication channels.

```mermaid
sequenceDiagram
participant Browser as "Browser"
participant FE as "Frontend API Client<br/>frontend/src/lib/api.ts"
participant Supa as "Supabase Auth<br/>frontend/src/lib/supabase.ts"
participant BE as "Backend API<br/>backend/app/main.py"
participant Auth as "JWT Verifier<br/>backend/app/core/auth.py"
participant Sec as "Security Verifiers<br/>backend/app/core/security.py"
Browser->>FE : "User navigates and interacts"
FE->>Supa : "Get session and access token"
Supa-->>FE : "Session with access token"
FE->>BE : "Authenticated request with Bearer token"
BE->>Auth : "Verify JWT"
Auth-->>BE : "Authenticated user claims"
BE-->>FE : "Response data"
Note over FE,BE : "CORS and middleware configured in backend"
```

**Diagram sources**
- [frontend/src/lib/api.ts:177-214](file://frontend/src/lib/api.ts#L177-L214)
- [frontend/src/lib/supabase.ts:15-25](file://frontend/src/lib/supabase.ts#L15-L25)
- [backend/app/main.py:14-22](file://backend/app/main.py#L14-L22)
- [backend/app/core/auth.py:22-69](file://backend/app/core/auth.py#L22-L69)

## Detailed Component Analysis

### Backend Configuration and Security
- Settings Model
  - Defines environment variables for app, database, Redis, CORS, Supabase, JWT, worker callback, email, shared contract, and OpenRouter.
  - Validates email settings when notifications are enabled.
  - Parses CORS origins into a list for middleware.

- CORS Middleware
  - Configured with allow_origins from settings, regex support for chrome-extension, credentials, and wildcard methods/headers.

- JWT Verification
  - Uses JWK client to verify Supabase access tokens with configurable audience and optional issuer.
  - Falls back to a shared JWT secret if provided.

- Worker Secret Verification
  - Enforces X-Worker-Secret header for internal worker callbacks.

- Extension Token Verification
  - Hashes extension token and validates against stored hashes in the database.

```mermaid
classDiagram
class Settings {
+string app_env
+bool app_dev_mode
+int api_port
+string app_url
+string database_url
+string redis_url
+string cors_origins
+string supabase_url
+string supabase_external_url
+string supabase_auth_jwks_url
+string supabase_jwt_secret
+string supabase_jwt_audience
+string supabase_jwt_issuer
+string worker_callback_secret
+float duplicate_similarity_threshold
+bool email_notifications_enabled
+string resend_api_key
+string email_from
+string shared_contract_path
+string openrouter_api_key
+string openrouter_cleanup_model
+cors_origin_list() string[]
}
class AuthVerifier {
+verify_token(token) AuthenticatedUser
-_decode(token) dict
}
class ExtensionAuthenticatedUser {
+string id
+string email
}
Settings <.. AuthVerifier : "provides JWKS/JWT config"
```

**Diagram sources**
- [backend/app/core/config.py:35-96](file://backend/app/core/config.py#L35-L96)
- [backend/app/core/auth.py:22-69](file://backend/app/core/auth.py#L22-L69)
- [backend/app/core/security.py:25-54](file://backend/app/core/security.py#L25-L54)

**Section sources**
- [backend/app/core/config.py:35-96](file://backend/app/core/config.py#L35-L96)
- [backend/app/main.py:14-22](file://backend/app/main.py#L14-L22)
- [backend/app/core/auth.py:22-69](file://backend/app/core/auth.py#L22-L69)
- [backend/app/core/security.py:13-54](file://backend/app/core/security.py#L13-L54)

### Frontend Environment and Authentication
- Environment Validation
  - Enforces presence of VITE_APP_ENV, VITE_APP_DEV_MODE, VITE_SUPABASE_URL, VITE_SUPABASE_ANON_KEY, and VITE_API_URL.
  - Transforms VITE_APP_DEV_MODE to boolean.

- Supabase Client
  - Creates a Supabase client with session persistence, auto-refresh, and sessionStorage for auth state.

- Protected Routes
  - Checks session state and redirects unauthenticated users to login.

- API Client
  - Retrieves access token from Supabase session and attaches Authorization header to all requests to the backend API.

```mermaid
flowchart TD
Start(["Initialize Frontend"]) --> LoadEnv["Load and validate env schema"]
LoadEnv --> InitSupabase["Create Supabase client with session options"]
InitSupabase --> ProtectedRoute["Check auth state on route change"]
ProtectedRoute --> HasSession{"Has session?"}
HasSession --> |No| Redirect["Redirect to login"]
HasSession --> |Yes| FetchToken["Fetch access token from session"]
FetchToken --> MakeRequest["Make authenticated request to backend"]
MakeRequest --> End(["Render UI"])
```

**Diagram sources**
- [frontend/src/lib/env.ts:1-15](file://frontend/src/lib/env.ts#L1-L15)
- [frontend/src/lib/supabase.ts:15-25](file://frontend/src/lib/supabase.ts#L15-L25)
- [frontend/src/routes/ProtectedRoute.tsx:6-43](file://frontend/src/routes/ProtectedRoute.tsx#L6-L43)
- [frontend/src/lib/api.ts:177-214](file://frontend/src/lib/api.ts#L177-L214)

**Section sources**
- [frontend/src/lib/env.ts:1-15](file://frontend/src/lib/env.ts#L1-L15)
- [frontend/src/lib/supabase.ts:1-26](file://frontend/src/lib/supabase.ts#L1-L26)
- [frontend/src/routes/ProtectedRoute.tsx:1-44](file://frontend/src/routes/ProtectedRoute.tsx#L1-L44)
- [frontend/src/lib/api.ts:177-214](file://frontend/src/lib/api.ts#L177-L214)

### Chrome Extension Integration
- Manifest Permissions
  - Declares permissions for activeTab, storage, tabs, and host access to all URLs.

- Popup Behavior
  - Captures current tab content via content script messaging.
  - Sends captured data to backend with X-Extension-Token header.
  - Handles unauthorized responses by clearing stored token and prompting reconnection.

```mermaid
sequenceDiagram
participant Ext as "Extension Popup<br/>frontend/public/chrome-extension/popup.js"
participant Content as "Content Script"
participant FE as "Frontend API<br/>frontend/src/lib/api.ts"
participant BE as "Backend API<br/>backend/app/api/session.py"
Ext->>Content : "CAPTURE_CURRENT_PAGE"
Content-->>Ext : "capture payload"
Ext->>FE : "POST /api/extension/import with X-Extension-Token"
FE->>BE : "Forward import request"
BE-->>FE : "Response (may be 401)"
FE-->>Ext : "Handle response and redirect"
```

**Diagram sources**
- [frontend/public/chrome-extension/manifest.json:1-24](file://frontend/public/chrome-extension/manifest.json#L1-L24)
- [frontend/public/chrome-extension/popup.js:109-135](file://frontend/public/chrome-extension/popup.js#L109-L135)
- [frontend/src/lib/api.ts:312-326](file://frontend/src/lib/api.ts#L312-L326)

**Section sources**
- [frontend/public/chrome-extension/manifest.json:1-24](file://frontend/public/chrome-extension/manifest.json#L1-L24)
- [frontend/public/chrome-extension/popup.js:1-156](file://frontend/public/chrome-extension/popup.js#L1-L156)
- [frontend/src/lib/api.ts:312-326](file://frontend/src/lib/api.ts#L312-L326)

### Agent Configuration and Callback Security
- Worker Settings
  - Loads environment variables for Redis, backend API URL, worker callback secret, shared contract path, OpenRouter configuration, and model names.
  - Validates presence of required OpenRouter and model configuration before use.

- Backend Callback Client
  - Sends callback events to backend with X-Worker-Secret header.
  - Requires WORKER_CALLBACK_SECRET to be configured.

```mermaid
flowchart TD
A["Worker Job Starts"] --> B["Load WorkerSettingsEnv"]
B --> C{"Secret configured?"}
C --> |No| E["Raise runtime error"]
C --> |Yes| D["Send callback to backend with X-Worker-Secret"]
D --> F["Backend verifies secret and processes event"]
```

**Diagram sources**
- [agents/worker.py:54-71](file://agents/worker.py#L54-L71)
- [agents/worker.py:290-305](file://agents/worker.py#L290-L305)

**Section sources**
- [agents/worker.py:54-71](file://agents/worker.py#L54-L71)
- [agents/worker.py:290-305](file://agents/worker.py#L290-L305)

## Dependency Analysis
This section maps environment variable dependencies across components and highlights integration points.

```mermaid
graph TB
subgraph "Environment Variables"
ENV_FE["VITE_SUPABASE_URL<br/>VITE_SUPABASE_ANON_KEY<br/>VITE_API_URL"]
ENV_BE["APP_ENV<br/>APP_DEV_MODE<br/>API_PORT<br/>APP_URL<br/>DATABASE_URL<br/>REDIS_URL<br/>CORS_ORIGINS<br/>SUPABASE_URL<br/>SUPABASE_EXTERNAL_URL<br/>SUPABASE_AUTH_JWKS_URL<br/>SUPABASE_JWT_SECRET<br/>SUPABASE_JWT_AUDIENCE<br/>SUPABASE_JWT_ISSUER<br/>WORKER_CALLBACK_SECRET<br/>EMAIL_NOTIFICATIONS_ENABLED<br/>RESEND_API_KEY<br/>EMAIL_FROM<br/>SHARED_CONTRACT_PATH<br/>OPENROUTER_API_KEY<br/>OPENROUTER_CLEANUP_MODEL"]
ENV_AG["APP_ENV<br/>APP_DEV_MODE<br/>REDIS_URL<br/>BACKEND_API_URL<br/>WORKER_CALLBACK_SECRET<br/>OPENROUTER_API_KEY<br/>OPENROUTER_BASE_URL<br/>EXTRACTION_AGENT_MODEL<br/>EXTRACTION_AGENT_FALLBACK_MODEL<br/>GENERATION_AGENT_MODEL<br/>GENERATION_AGENT_FALLBACK_MODEL<br/>VALIDATION_AGENT_MODEL<br/>VALIDATION_AGENT_FALLBACK_MODEL"]
end
FE["frontend/src/lib/env.ts"] --> BE["backend/app/core/config.py"]
FE --> AG["agents/worker.py"]
BE --> AG
BE --> SUPA["Supabase Services"]
FE --> SUPA
```

**Diagram sources**
- [frontend/src/lib/env.ts:1-15](file://frontend/src/lib/env.ts#L1-L15)
- [backend/app/core/config.py:35-96](file://backend/app/core/config.py#L35-L96)
- [agents/worker.py:54-71](file://agents/worker.py#L54-L71)

**Section sources**
- [frontend/src/lib/env.ts:1-15](file://frontend/src/lib/env.ts#L1-L15)
- [backend/app/core/config.py:35-96](file://backend/app/core/config.py#L35-L96)
- [agents/worker.py:54-71](file://agents/worker.py#L54-L71)

## Performance Considerations
- Environment caching
  - Backend settings are cached to avoid repeated parsing and validation overhead.
- CORS configuration
  - Allow regex for chrome-extension reduces unnecessary preflight checks for extension contexts.
- Session handling
  - Frontend uses sessionStorage for auth state and auto-refresh tokens to minimize re-authentication friction.
- Worker callbacks
  - Short timeouts and explicit error handling prevent long-running tasks from blocking the pipeline.

[No sources needed since this section provides general guidance]

## Troubleshooting Guide
Common configuration issues and resolutions:

- Missing or invalid environment variables
  - Frontend: Ensure VITE_SUPABASE_URL, VITE_SUPABASE_ANON_KEY, VITE_API_URL are present and valid. The Zod schema will fail early if missing.
  - Backend: Validate DATABASE_URL, REDIS_URL, SUPABASE_AUTH_JWKS_URL, SUPABASE_JWT_SECRET, WORKER_CALLBACK_SECRET, and email notification settings when enabled.
  - Agents: Confirm OPENROUTER_API_KEY and model names are set; otherwise, runtime errors will occur during job execution.

- CORS errors
  - Verify CORS_ORIGINS includes the frontend origin and that APP_URL matches the frontend host. Backend CORS middleware uses allow_origins and allow_origin_regex.

- JWT verification failures
  - Ensure SUPABASE_AUTH_JWKS_URL is reachable and SUPABASE_JWT_SECRET is configured if JWK verification fails. The verifier attempts JWK verification first, then falls back to the shared secret.

- Worker callback unauthorized
  - Confirm WORKER_CALLBACK_SECRET is set consistently across agents and backend. Requests missing or mismatched X-Worker-Secret will be rejected.

- Extension token invalid
  - If the extension receives 401, the stored token is cleared. Reconnect the extension from the web app to issue a new token.

- Supabase service misconfiguration
  - Ensure GOTRUE_SITE_URL, GOTRUE_URI_ALLOW_LIST, and SUPABASE_URL align with APP_URL and APP_ENV. Kong gateway must be healthy and configured with the correct keys.

**Section sources**
- [frontend/src/lib/env.ts:1-15](file://frontend/src/lib/env.ts#L1-L15)
- [backend/app/core/config.py:35-96](file://backend/app/core/config.py#L35-L96)
- [backend/app/core/auth.py:22-69](file://backend/app/core/auth.py#L22-L69)
- [backend/app/core/security.py:13-54](file://backend/app/core/security.py#L13-L54)
- [agents/worker.py:290-305](file://agents/worker.py#L290-L305)
- [frontend/public/chrome-extension/popup.js:118-126](file://frontend/public/chrome-extension/popup.js#L118-L126)

## Conclusion
This document outlined the configuration and environment setup across the frontend, backend, and agents. By validating environment variables early, securing worker callbacks, enforcing CORS policies, and integrating Supabase authentication, the system achieves robust operation across development and production environments. Adhering to the best practices and troubleshooting steps herein will help maintain a secure and reliable deployment.

[No sources needed since this section summarizes without analyzing specific files]

## Appendices

### Environment Variable Reference

- Frontend (Vite)
  - VITE_APP_ENV: string, default "development"
  - VITE_APP_DEV_MODE: string transformed to boolean, default "false"
  - VITE_SUPABASE_URL: string, URL
  - VITE_SUPABASE_ANON_KEY: string, required
  - VITE_API_URL: string, URL

- Backend (Python)
  - APP_ENV: string, default "development"
  - APP_DEV_MODE: bool, default False
  - API_PORT: int, default 8000
  - APP_URL: string, default "http://localhost:5173"
  - DATABASE_URL: string, default local Postgres
  - REDIS_URL: string, default local Redis
  - CORS_ORIGINS: string, default frontend origin
  - SUPABASE_URL: string, default local Supabase
  - SUPABASE_EXTERNAL_URL: string, default local Supabase
  - SUPABASE_AUTH_JWKS_URL: string, default local JWKS
  - SUPABASE_JWT_SECRET: string, optional
  - SUPABASE_JWT_AUDIENCE: string, default "authenticated"
  - SUPABASE_JWT_ISSUER: string, optional
  - WORKER_CALLBACK_SECRET: string, optional
  - DUPLICATE_SIMILARITY_THRESHOLD: float, default 85.0
  - EMAIL_NOTIFICATIONS_ENABLED: bool, default False
  - RESEND_API_KEY: string, optional
  - EMAIL_FROM: string, optional
  - SHARED_CONTRACT_PATH: string, default shared path
  - OPENROUTER_API_KEY: string, optional
  - OPENROUTER_CLEANUP_MODEL: string, default model

- Agents (Python)
  - APP_ENV: string, default "development"
  - APP_DEV_MODE: bool, default False
  - REDIS_URL: string, default local Redis
  - BACKEND_API_URL: string, default backend service URL
  - WORKER_CALLBACK_SECRET: string, optional
  - OPENROUTER_API_KEY: string, optional
  - OPENROUTER_BASE_URL: string, default OpenRouter base URL
  - EXTRACTION_AGENT_MODEL: string, optional
  - EXTRACTION_AGENT_FALLBACK_MODEL: string, optional
  - GENERATION_AGENT_MODEL: string, optional
  - GENERATION_AGENT_FALLBACK_MODEL: string, optional
  - VALIDATION_AGENT_MODEL: string, optional
  - VALIDATION_AGENT_FALLBACK_MODEL: string, optional

**Section sources**
- [frontend/src/lib/env.ts:1-15](file://frontend/src/lib/env.ts#L1-L15)
- [backend/app/core/config.py:35-96](file://backend/app/core/config.py#L35-L96)
- [agents/worker.py:54-71](file://agents/worker.py#L54-L71)