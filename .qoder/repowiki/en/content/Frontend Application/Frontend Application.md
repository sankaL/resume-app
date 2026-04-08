# Frontend Application

<cite>
**Referenced Files in This Document**
- [main.tsx](file://frontend/src/main.tsx)
- [App.tsx](file://frontend/src/App.tsx)
- [AppShell.tsx](file://frontend/src/routes/AppShell.tsx)
- [ProtectedRoute.tsx](file://frontend/src/routes/ProtectedRoute.tsx)
- [ApplicationsDashboardPage.tsx](file://frontend/src/routes/ApplicationsDashboardPage.tsx)
- [ApplicationDetailPage.tsx](file://frontend/src/routes/ApplicationDetailPage.tsx)
- [ExtensionPage.tsx](file://frontend/src/routes/ExtensionPage.tsx)
- [ProfilePage.tsx](file://frontend/src/routes/ProfilePage.tsx)
- [LoginPage.tsx](file://frontend/src/routes/LoginPage.tsx)
- [button.tsx](file://frontend/src/components/ui/button.tsx)
- [card.tsx](file://frontend/src/components/ui/card.tsx)
- [input.tsx](file://frontend/src/components/ui/input.tsx)
- [label.tsx](file://frontend/src/components/ui/label.tsx)
- [api.ts](file://frontend/src/lib/api.ts)
- [supabase.ts](file://frontend/src/lib/supabase.ts)
- [env.ts](file://frontend/src/lib/env.ts)
- [utils.ts](file://frontend/src/lib/utils.ts)
- [package.json](file://frontend/package.json)
- [vite.config.ts](file://frontend/vite.config.ts)
- [tailwind.config.ts](file://frontend/tailwind.config.ts)
- [index.html](file://frontend/index.html)
- [chrome-extension manifest.json](file://frontend/public/chrome-extension/manifest.json)
- [chrome-extension content-script.js](file://frontend/public/chrome-extension/content-script.js)
- [chrome-extension service-worker.js](file://frontend/public/chrome-extension/service-worker.js)
- [chrome-extension popup.js](file://frontend/public/chrome-extension/popup.js)
- [chrome-extension popup.html](file://frontend/public/chrome-extension/popup.html)
- [chrome-extension popup.css](file://frontend/public/chrome-extension/popup.css)
- [chrome-extension-popup.d.ts](file://frontend/src/types/chrome-extension-popup.d.ts)
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
This document describes the React 19-based frontend application for the AI Resume Builder. It covers the application structure, routing with React Router DOM, state management patterns, component architecture, styling with Tailwind CSS, Chrome extension integration, authentication and session management, responsive design, accessibility, cross-browser compatibility, and integration with the backend API.

## Project Structure
The frontend is a Vite-powered React application configured with TypeScript and Tailwind CSS. It uses React Router DOM for client-side routing and @supabase/supabase-js for authentication and session persistence. The application is organized into:
- Routes: Page-level components under src/routes
- Components: Reusable UI primitives under src/components/ui
- Library: API clients, environment configuration, and utilities under src/lib
- Public assets: Chrome extension code under frontend/public/chrome-extension

```mermaid
graph TB
A["main.tsx<br/>Bootstraps React and Router"] --> B["App.tsx<br/>Top-level Routes"]
B --> C["ProtectedRoute.tsx<br/>Auth gating"]
C --> D["AppShell.tsx<br/>Layout shell"]
D --> E["ApplicationsDashboardPage.tsx"]
D --> F["ApplicationDetailPage.tsx"]
D --> G["ExtensionPage.tsx"]
D --> H["ProfilePage.tsx"]
B --> I["LoginPage.tsx"]
D --> J["button.tsx / card.tsx / input.tsx / label.tsx"]
K["api.ts<br/>Authenticated HTTP client"] --> L["supabase.ts<br/>Supabase client"]
M["env.ts<br/>Environment variables"] --> K
N["tailwind.config.ts<br/>Theme and colors"] --> O["index.css<br/>Global styles"]
P["vite.config.ts<br/>Aliases and test setup"] --> Q["package.json<br/>Dependencies and scripts"]
```

**Diagram sources**
- [main.tsx:1-14](file://frontend/src/main.tsx#L1-L14)
- [App.tsx:1-36](file://frontend/src/App.tsx#L1-L36)
- [ProtectedRoute.tsx:1-44](file://frontend/src/routes/ProtectedRoute.tsx#L1-L44)
- [AppShell.tsx:1-89](file://frontend/src/routes/AppShell.tsx#L1-L89)
- [ApplicationsDashboardPage.tsx:1-264](file://frontend/src/routes/ApplicationsDashboardPage.tsx#L1-L264)
- [ApplicationDetailPage.tsx:1-1101](file://frontend/src/routes/ApplicationDetailPage.tsx#L1-L1101)
- [ExtensionPage.tsx:1-200](file://frontend/src/routes/ExtensionPage.tsx#L1-L200)
- [ProfilePage.tsx:1-264](file://frontend/src/routes/ProfilePage.tsx#L1-L264)
- [LoginPage.tsx:1-111](file://frontend/src/routes/LoginPage.tsx#L1-L111)
- [button.tsx:1-23](file://frontend/src/components/ui/button.tsx#L1-L23)
- [card.tsx](file://frontend/src/components/ui/card.tsx)
- [input.tsx](file://frontend/src/components/ui/input.tsx)
- [label.tsx](file://frontend/src/components/ui/label.tsx)
- [api.ts:1-489](file://frontend/src/lib/api.ts#L1-L489)
- [supabase.ts:1-26](file://frontend/src/lib/supabase.ts#L1-L26)
- [env.ts](file://frontend/src/lib/env.ts)
- [utils.ts](file://frontend/src/lib/utils.ts)
- [tailwind.config.ts:1-25](file://frontend/tailwind.config.ts#L1-L25)
- [vite.config.ts:1-24](file://frontend/vite.config.ts#L1-L24)
- [package.json:1-38](file://frontend/package.json#L1-L38)

**Section sources**
- [main.tsx:1-14](file://frontend/src/main.tsx#L1-L14)
- [App.tsx:1-36](file://frontend/src/App.tsx#L1-L36)
- [vite.config.ts:1-24](file://frontend/vite.config.ts#L1-L24)
- [tailwind.config.ts:1-25](file://frontend/tailwind.config.ts#L1-L25)
- [package.json:1-38](file://frontend/package.json#L1-L38)

## Core Components
- AppShell: Provides the main layout, navigation, session bootstrap, and sign-out flow.
- ProtectedRoute: Guards protected routes using Supabase auth state.
- UI primitives: Button, Card, Input, Label provide consistent styling and behavior.
- Pages: Dashboard, Application Detail, Extension, Profile, Login.

Key patterns:
- Centralized API client with bearer token injection via Supabase session.
- Deferred UI updates using useDeferredValue for search performance.
- Controlled forms with optimistic UI updates and rollback on errors.
- Polling for long-running operations (extraction and generation progress).

**Section sources**
- [AppShell.tsx:1-89](file://frontend/src/routes/AppShell.tsx#L1-L89)
- [ProtectedRoute.tsx:1-44](file://frontend/src/routes/ProtectedRoute.tsx#L1-L44)
- [button.tsx:1-23](file://frontend/src/components/ui/button.tsx#L1-L23)
- [ApplicationsDashboardPage.tsx:1-264](file://frontend/src/routes/ApplicationsDashboardPage.tsx#L1-L264)
- [ApplicationDetailPage.tsx:1-1101](file://frontend/src/routes/ApplicationDetailPage.tsx#L1-L1101)
- [ExtensionPage.tsx:1-200](file://frontend/src/routes/ExtensionPage.tsx#L1-L200)
- [ProfilePage.tsx:1-264](file://frontend/src/routes/ProfilePage.tsx#L1-L264)
- [api.ts:177-238](file://frontend/src/lib/api.ts#L177-L238)

## Architecture Overview
The frontend follows a layered architecture:
- Presentation layer: React components and pages
- Routing layer: React Router DOM with nested routes and guards
- State layer: React hooks for local component state; Supabase for auth session
- Data layer: API module wraps authenticated requests to the backend
- Infrastructure: Tailwind CSS for styling, Vite for build tooling

```mermaid
graph TB
subgraph "Presentation"
R["Routes and Pages"]
U["UI Components"]
end
subgraph "Routing"
RR["React Router DOM"]
end
subgraph "State"
SR["Supabase Auth"]
end
subgraph "Data"
AC["Authenticated Client (api.ts)"]
BE["Backend API"]
end
subgraph "Infrastructure"
TW["Tailwind CSS"]
VT["Vite Build"]
end
R --> RR
U --> TW
RR --> SR
R --> AC
AC --> BE
SR --> AC
VT --> R
```

**Diagram sources**
- [App.tsx:1-36](file://frontend/src/App.tsx#L1-L36)
- [ProtectedRoute.tsx:1-44](file://frontend/src/routes/ProtectedRoute.tsx#L1-L44)
- [api.ts:177-238](file://frontend/src/lib/api.ts#L177-L238)
- [supabase.ts:1-26](file://frontend/src/lib/supabase.ts#L1-L26)
- [tailwind.config.ts:1-25](file://frontend/tailwind.config.ts#L1-L25)
- [vite.config.ts:1-24](file://frontend/vite.config.ts#L1-L24)

## Detailed Component Analysis

### Authentication and Session Management
- Supabase client is initialized once and configured for session persistence and token refresh.
- ProtectedRoute checks session state on mount and subscribes to auth state changes.
- LoginPage signs in with email/password and redirects to the app shell.
- AppShell fetches session bootstrap data and exposes sign-out.

```mermaid
sequenceDiagram
participant Browser as "Browser"
participant Supabase as "Supabase Client"
participant Protected as "ProtectedRoute"
participant Shell as "AppShell"
Browser->>Supabase : "getSession()"
Supabase-->>Protected : "Session state"
Protected->>Protected : "Set isAuthenticated"
Protected-->>Browser : "Render <AppShell> or <Navigate to /login>"
Shell->>Supabase : "auth.signOut()"
Supabase-->>Shell : "Session cleared"
Shell-->>Browser : "Redirect to /login"
```

**Diagram sources**
- [ProtectedRoute.tsx:10-26](file://frontend/src/routes/ProtectedRoute.tsx#L10-L26)
- [supabase.ts:15-25](file://frontend/src/lib/supabase.ts#L15-L25)
- [AppShell.tsx:24-28](file://frontend/src/routes/AppShell.tsx#L24-L28)
- [LoginPage.tsx:17-36](file://frontend/src/routes/LoginPage.tsx#L17-L36)

**Section sources**
- [supabase.ts:1-26](file://frontend/src/lib/supabase.ts#L1-L26)
- [ProtectedRoute.tsx:1-44](file://frontend/src/routes/ProtectedRoute.tsx#L1-L44)
- [LoginPage.tsx:1-111](file://frontend/src/routes/LoginPage.tsx#L1-L111)
- [AppShell.tsx:1-89](file://frontend/src/routes/AppShell.tsx#L1-L89)

### Routing Configuration
- Top-level routes define login and the protected app shell.
- AppShell nests dashboard, application detail, extension, profile, and resume routes.
- ProtectedRoute ensures only authenticated users can access nested routes.

```mermaid
flowchart TD
Root["<App> Routes"] --> Login["/login"]
Root --> App["/app (ProtectedRoute)"]
App --> Dashboard["/app (index)"]
App --> Detail["/app/applications/:id"]
App --> Extension["/app/extension"]
App --> Profile["/app/profile"]
App --> Resumes["/app/resumes"]
App --> NewResume["/app/resumes/new"]
App --> EditResume["/app/resumes/:id"]
Root --> Wildcard["* -> /app"]
```

**Diagram sources**
- [App.tsx:12-34](file://frontend/src/App.tsx#L12-L34)

**Section sources**
- [App.tsx:1-36](file://frontend/src/App.tsx#L1-L36)
- [ProtectedRoute.tsx:1-44](file://frontend/src/routes/ProtectedRoute.tsx#L1-L44)

### Applications Dashboard
- Lists applications with filtering, sorting, and search.
- Creates new applications from job URLs.
- Toggles applied state with optimistic updates and rollback on error.
- Shows status badges and action-required indicators.

```mermaid
flowchart TD
Start(["Dashboard Mount"]) --> Load["Fetch applications"]
Load --> Render["Render cards with filters"]
Render --> Create["Submit job URL form"]
Create --> Submit["POST /api/applications"]
Submit --> Navigate["Navigate to detail page"]
Render --> Toggle["Toggle 'Applied' checkbox"]
Toggle --> Patch["PATCH /api/applications/:id"]
Patch --> Update["Optimistically update UI"]
Patch --> Error{"Request OK?"}
Error --> |No| Rollback["Restore previous state"]
Error --> |Yes| Continue["Show updated state"]
```

**Diagram sources**
- [ApplicationsDashboardPage.tsx:27-96](file://frontend/src/routes/ApplicationsDashboardPage.tsx#L27-L96)
- [api.ts:244-267](file://frontend/src/lib/api.ts#L244-L267)

**Section sources**
- [ApplicationsDashboardPage.tsx:1-264](file://frontend/src/routes/ApplicationsDashboardPage.tsx#L1-L264)
- [api.ts:244-267](file://frontend/src/lib/api.ts#L244-L267)

### Application Detail
- Loads application detail and progress, polls for extraction/generation updates.
- Handles manual entry, retry extraction, duplicate review, and generation controls.
- Manages resume draft editing and PDF export.

```mermaid
sequenceDiagram
participant Page as "ApplicationDetailPage"
participant API as "api.ts"
participant BE as "Backend"
participant Timer as "Window Intervals"
Page->>API : "fetchApplicationDetail(id)"
API->>BE : "GET /api/applications/ : id"
BE-->>API : "ApplicationDetail"
API-->>Page : "Detail state"
Page->>Timer : "Start polling for progress"
loop Every 2s while extracting/generating
Page->>API : "fetchApplicationProgress(id)"
API->>BE : "GET /api/applications/ : id/progress"
BE-->>API : "ExtractionProgress"
API-->>Page : "Progress state"
end
Page->>API : "triggerGeneration/settings"
API->>BE : "POST /api/applications/ : id/generate"
BE-->>API : "Updated ApplicationDetail"
API-->>Page : "Refresh detail and draft"
```

**Diagram sources**
- [ApplicationDetailPage.tsx:88-152](file://frontend/src/routes/ApplicationDetailPage.tsx#L88-L152)
- [api.ts:255-300](file://frontend/src/lib/api.ts#L255-L300)
- [api.ts:414-427](file://frontend/src/lib/api.ts#L414-L427)

**Section sources**
- [ApplicationDetailPage.tsx:1-1101](file://frontend/src/routes/ApplicationDetailPage.tsx#L1-L1101)
- [api.ts:414-488](file://frontend/src/lib/api.ts#L414-L488)

### Chrome Extension Integration
- ExtensionPage manages connection lifecycle: issue token, revoke token, and listen for bridge messages.
- Uses postMessage to communicate with the extension popup and content script.
- Demonstrates scoped token usage without exposing Supabase session.

```mermaid
sequenceDiagram
participant Web as "Web App"
participant Ext as "Chrome Extension"
participant API as "api.ts"
participant BE as "Backend"
Web->>Ext : "postMessage REQUEST_EXTENSION_STATUS"
Ext-->>Web : "postMessage EXTENSION_STATUS {connected, appUrl}"
Web->>API : "issueExtensionToken()"
API->>BE : "POST /api/extension/token"
BE-->>API : "{token, status}"
API-->>Web : "Token and status"
Web->>Ext : "postMessage CONNECT_EXTENSION_TOKEN {token, appUrl}"
Web->>API : "revokeExtensionToken()"
API->>BE : "DELETE /api/extension/token"
BE-->>API : "status"
API-->>Web : "status"
Web->>Ext : "postMessage REVOKE_EXTENSION_TOKEN {appUrl}"
```

**Diagram sources**
- [ExtensionPage.tsx:35-125](file://frontend/src/routes/ExtensionPage.tsx#L35-L125)
- [api.ts:312-326](file://frontend/src/lib/api.ts#L312-L326)
- [chrome-extension manifest.json](file://frontend/public/chrome-extension/manifest.json)
- [chrome-extension content-script.js](file://frontend/public/chrome-extension/content-script.js)
- [chrome-extension service-worker.js](file://frontend/public/chrome-extension/service-worker.js)
- [chrome-extension popup.js](file://frontend/public/chrome-extension/popup.js)
- [chrome-extension popup.html](file://frontend/public/chrome-extension/popup.html)
- [chrome-extension popup.css](file://frontend/public/chrome-extension/popup.css)

**Section sources**
- [ExtensionPage.tsx:1-200](file://frontend/src/routes/ExtensionPage.tsx#L1-L200)
- [api.ts:312-326](file://frontend/src/lib/api.ts#L312-L326)
- [chrome-extension manifest.json](file://frontend/public/chrome-extension/manifest.json)
- [chrome-extension content-script.js](file://frontend/public/chrome-extension/content-script.js)
- [chrome-extension service-worker.js](file://frontend/public/chrome-extension/service-worker.js)
- [chrome-extension popup.js](file://frontend/public/chrome-extension/popup.js)
- [chrome-extension popup.html](file://frontend/public/chrome-extension/popup.html)
- [chrome-extension popup.css](file://frontend/public/chrome-extension/popup.css)

### Profile Management
- Loads profile data on mount and supports updating personal info and section preferences.
- Tracks dirty state and provides save/cancel behavior with optimistic updates.

**Section sources**
- [ProfilePage.tsx:1-264](file://frontend/src/routes/ProfilePage.tsx#L1-L264)
- [api.ts:401-410](file://frontend/src/lib/api.ts#L401-L410)

### Styling Approach
- Tailwind CSS with custom theme tokens for colors, fonts, and shadows.
- Utility-first classes applied directly in components for rapid iteration.
- Responsive breakpoints and spacing scales ensure consistent layouts across devices.

**Section sources**
- [tailwind.config.ts:1-25](file://frontend/tailwind.config.ts#L1-L25)
- [button.tsx:1-23](file://frontend/src/components/ui/button.tsx#L1-L23)
- [card.tsx](file://frontend/src/components/ui/card.tsx)
- [input.tsx](file://frontend/src/components/ui/input.tsx)
- [label.tsx](file://frontend/src/components/ui/label.tsx)

## Dependency Analysis
- React 19 and React Router DOM power the UI and routing.
- @supabase/supabase-js handles authentication and session persistence.
- Tailwind CSS provides styling; Vite builds the app and aliases paths.
- The API module centralizes authenticated requests and error handling.

```mermaid
graph LR
React["react@^19.1.0"] --> App["App.tsx"]
Router["react-router-dom@^7.6.1"] --> App
Supabase["@supabase/supabase-js@^2.49.8"] --> Auth["supabase.ts"]
Auth --> API["api.ts"]
API --> Backend["Backend API"]
Tailwind["tailwindcss@^3.4.17"] --> Styles["tailwind.config.ts"]
Vite["vite@^6.2.4"] --> Build["vite.config.ts"]
Types["typescript@^5.8.3"] --> TSConfig["tsconfig.app.json"]
```

**Diagram sources**
- [package.json:13-21](file://frontend/package.json#L13-L21)
- [api.ts:1-2](file://frontend/src/lib/api.ts#L1-L2)
- [supabase.ts:1-2](file://frontend/src/lib/supabase.ts#L1-L2)
- [tailwind.config.ts:1-25](file://frontend/tailwind.config.ts#L1-L25)
- [vite.config.ts:1-24](file://frontend/vite.config.ts#L1-L24)

**Section sources**
- [package.json:1-38](file://frontend/package.json#L1-L38)
- [vite.config.ts:1-24](file://frontend/vite.config.ts#L1-L24)
- [tailwind.config.ts:1-25](file://frontend/tailwind.config.ts#L1-L25)

## Performance Considerations
- useDeferredValue for search input reduces re-renders during typing.
- Optimistic UI updates followed by server sync improve perceived responsiveness.
- Polling intervals are conservative (every 2 seconds) to balance UX and resource usage.
- Tailwind JIT compilation and minimal CSS reduce bundle size.

## Troubleshooting Guide
Common issues and resolutions:
- Authentication failures: Verify Supabase credentials and session persistence. Check auth state change subscriptions and token availability.
- API request errors: Inspect network tab for 4xx/5xx responses; the API module surfaces detailed error messages from the backend.
- Extension bridge not detected: Confirm manifest permissions, service worker registration, and popup messaging setup.
- Styling inconsistencies: Ensure Tailwind content paths include all component files and rebuild the project.

**Section sources**
- [api.ts:190-214](file://frontend/src/lib/api.ts#L190-L214)
- [ExtensionPage.tsx:43-72](file://frontend/src/routes/ExtensionPage.tsx#L43-L72)
- [tailwind.config.ts:4-5](file://frontend/tailwind.config.ts#L4-L5)

## Conclusion
The frontend application is a modular, authenticated React 19 app with clear separation of concerns. It leverages Supabase for authentication, React Router for navigation, and a centralized API client for backend integration. The UI is built with reusable components and Tailwind CSS, ensuring a consistent and responsive design. The Chrome extension integration demonstrates secure, scoped communication for job capture. Together, these patterns support maintainability, scalability, and a robust user experience.

## Appendices

### Component Class Diagram
```mermaid
classDiagram
class ProtectedRoute {
+children
+isLoading : boolean
+isAuthenticated : boolean
+useEffect()
}
class AppShell {
+bootstrap
+error
+handleSignOut()
}
class ApplicationsDashboardPage {
+applications
+search
+statusFilter
+sortMode
+handleCreateApplication()
+handleAppliedToggle()
}
class ApplicationDetailPage {
+detail
+progress
+draft
+handleSaveJobInfo()
+handleTriggerGeneration()
+handleExportPdf()
}
class ExtensionPage {
+status
+bridgeDetected
+handleConnect()
+handleRevoke()
}
class ProfilePage {
+profile
+sectionPreferences
+handleSave()
}
class LoginPage {
+email
+password
+handleSubmit()
}
class Button
class Card
class Input
class Label
ProtectedRoute --> AppShell : "wraps"
AppShell --> ApplicationsDashboardPage : "renders"
AppShell --> ApplicationDetailPage : "renders"
AppShell --> ExtensionPage : "renders"
AppShell --> ProfilePage : "renders"
LoginPage --> ProtectedRoute : "redirects to"
ApplicationsDashboardPage --> Button : "uses"
ApplicationsDashboardPage --> Card : "uses"
ApplicationDetailPage --> Button : "uses"
ApplicationDetailPage --> Card : "uses"
ApplicationDetailPage --> Input : "uses"
ExtensionPage --> Button : "uses"
ExtensionPage --> Card : "uses"
ProfilePage --> Button : "uses"
ProfilePage --> Card : "uses"
ProfilePage --> Input : "uses"
LoginPage --> Button : "uses"
LoginPage --> Card : "uses"
LoginPage --> Input : "uses"
LoginPage --> Label : "uses"
```

**Diagram sources**
- [ProtectedRoute.tsx:6-43](file://frontend/src/routes/ProtectedRoute.tsx#L6-L43)
- [AppShell.tsx:8-88](file://frontend/src/routes/AppShell.tsx#L8-L88)
- [ApplicationsDashboardPage.tsx:16-263](file://frontend/src/routes/ApplicationsDashboardPage.tsx#L16-L263)
- [ApplicationDetailPage.tsx:38-1101](file://frontend/src/routes/ApplicationDetailPage.tsx#L38-L1101)
- [ExtensionPage.tsx:26-199](file://frontend/src/routes/ExtensionPage.tsx#L26-L199)
- [ProfilePage.tsx:17-263](file://frontend/src/routes/ProfilePage.tsx#L17-L263)
- [LoginPage.tsx:10-110](file://frontend/src/routes/LoginPage.tsx#L10-L110)
- [button.tsx:8-22](file://frontend/src/components/ui/button.tsx#L8-L22)
- [card.tsx](file://frontend/src/components/ui/card.tsx)
- [input.tsx](file://frontend/src/components/ui/input.tsx)
- [label.tsx](file://frontend/src/components/ui/label.tsx)

### Accessibility and Responsive Design
- Semantic HTML and proper labeling via Label components.
- Keyboard navigable buttons and form controls.
- Sufficient color contrast and readable typography scales.
- Responsive grids and flexible layouts adapt to mobile and desktop.

**Section sources**
- [button.tsx:1-23](file://frontend/src/components/ui/button.tsx#L1-L23)
- [input.tsx](file://frontend/src/components/ui/input.tsx)
- [label.tsx](file://frontend/src/components/ui/label.tsx)
- [tailwind.config.ts:6-21](file://frontend/tailwind.config.ts#L6-L21)

### Cross-Browser Compatibility
- Modern JavaScript features supported by Vite and React 19.
- Tailwind utilities provide consistent rendering across browsers.
- PostCSS and autoprefixer ensure vendor prefixes where needed.

**Section sources**
- [package.json:29-35](file://frontend/package.json#L29-L35)
- [tailwind.config.ts:1-25](file://frontend/tailwind.config.ts#L1-L25)