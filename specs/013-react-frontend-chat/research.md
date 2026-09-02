# Phase 0 Research: React Frontend Chat Experience

## Decision 1: Scaffold as a separate top-level frontend/ app using Vite react-ts
- Decision: Create `frontend/` at repository root via Vite `react-ts` template.
- Rationale: Matches NFR-002 and keeps frontend lifecycle isolated from backend runtime concerns.
- Alternatives considered:
  - Embed static templates inside backend: rejected due weak TypeScript/Tailwind integration and slower UI iteration.
  - Monorepo tool migration: rejected as unnecessary for this pass.

## Decision 2: TailwindCSS via PostCSS-integrated build pipeline
- Decision: Use standard Vite + Tailwind + PostCSS integration (tailwind config + postcss config), not CDN styles.
- Rationale: Provides deterministic production builds and aligns with frontend stack requirements.
- Alternatives considered:
  - Tailwind CDN runtime injection: rejected because it bypasses build-time processing and requirement constraints.

## Decision 3: Use fetch + ReadableStream parser for POST stream
- Decision: Implement chat stream client with `fetch()` POST and manual `data:` line parsing from `ReadableStream` chunks.
- Rationale: Existing endpoint is POST `/chat/stream`; native EventSource cannot send POST with JSON body.
- Alternatives considered:
  - EventSource API: rejected due GET-only limitation.
  - WebSocket proxy: rejected because backend contract must remain unchanged.

## Decision 4: Typed event and payload modeling from existing backend schemas
- Decision: Define TypeScript interfaces mirroring backend `ChatStreamEvent`, `TicketStatusResponse`, `PasswordResetResponse`, and `TicketCreateResponse`.
- Rationale: Maintains schema discipline and safe UI rendering paths for tool outputs.
- Alternatives considered:
  - Unstructured `any` payload handling: rejected because it increases runtime errors and inconsistent rendering.

## Decision 5: Tool-call rendering with three explicit card components
- Decision: Parse JSON-encoded `tool_call` payload and map to typed UI cards (ticket status, password reset, ticket creation).
- Rationale: Satisfies US-007 requirement for structured user-facing action results.
- Alternatives considered:
  - Raw JSON pretty-print: rejected by explicit requirement and poor UX.
  - Single generic key/value table only: rejected for weaker semantic clarity.

## Decision 6: Health checks are informational only for this slice
- Decision: Do not gate send flow on `/health`; treat health/readiness and fetch failures through the same safe error-display path.
- Rationale: Matches clarified behavior (Option C) and preserves user ability to retry without blocking UI.
- Alternatives considered:
  - Hard health gate: rejected by clarification.
  - Continuous polling with status lock: rejected as out of scope.

## Decision 7: Session identity generated on mount and held in state
- Decision: Generate `user_id` and `session_id` using `crypto.randomUUID()` on initial load and send with each request.
- Rationale: Meets frontend continuity requirement without introducing authentication scope.
- Alternatives considered:
  - Server-assigned session bootstrap endpoint: rejected due no-backend-change rule.
  - Local storage persistence across browser restarts: deferred as out of scope.

## Decision 8: Manual verification over additional test framework setup
- Decision: Rely on manual walkthrough verification for this pass and avoid adding extra frontend test tooling.
- Rationale: Aligns with requested scope and keeps implementation focused on core UX and stream behavior.
- Alternatives considered:
  - Add Vitest/RTL/Cypress setup now: rejected as beyond requested pass scope.
