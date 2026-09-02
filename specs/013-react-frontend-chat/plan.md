# Implementation Plan: React Frontend Chat Experience

**Branch**: `[013-react-frontend-chat]` | **Date**: 2026-09-01 | **Spec**: [/specs/013-react-frontend-chat/spec.md](/specs/013-react-frontend-chat/spec.md)

**Input**: Feature specification from `/specs/013-react-frontend-chat/spec.md`

## Summary

Create a new top-level `frontend/` application using Vite `react-ts` with TailwindCSS via build-integrated PostCSS. Implement a single-page chat interface that POSTs to `/chat/stream` and parses SSE-style `data:` lines via `fetch()` + `ReadableStream`, streams token output into assistant bubbles, renders typed tool-call cards for three backend tool payloads, handles errors safely, and keeps per-page-session identity using `crypto.randomUUID()` without any backend changes.

## Technical Context

**Language/Version**: TypeScript 5.x + React 18 (Vite react-ts scaffold), Node.js 20 LTS for tooling

**Primary Dependencies**: Vite, React, TailwindCSS, PostCSS, Autoprefixer

**Storage**: Browser in-memory component state only (conversation list, loading state, per-page identifiers)

**Testing**: Manual browser walkthrough for this pass; no additional frontend test framework beyond Vite defaults

**Target Platform**: Modern desktop browsers for local dev and MVP verification

**Project Type**: Web frontend application consuming existing backend endpoints

**Performance Goals**:
- Stream token updates incrementally so users perceive immediate assistant progress.
- Keep UI responsive while parsing chunked stream data and rendering conversation updates.

**Constraints**:
- Scaffold `frontend/` with Vite `react-ts` and TailwindCSS standard integration (PostCSS pipeline, not CDN).
- Implement only frontend modules under `frontend/src/api`, `frontend/src/types`, `frontend/src/components`, and `frontend/src/App.tsx` wiring.
- Use `fetch()` + `ReadableStream` for POST stream parsing; do not use native EventSource.
- No health-check polling or gating; fetch/network failures and backend error events share error-display path.
- No backend modifications, no new endpoints, no auth/login, no cross-session history browsing, no long-term memory UI, no Arize/Promptfoo UI.

**Scale/Scope**: One frontend slice enabling end-to-end manual walkthrough across existing backend stages with structured UI for tool and error events.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Pre-Phase 0 gate review:
1. Vertical slice first: PASS. Delivers complete browser-to-existing-backend journey without waiting on additional infrastructure.
2. RAG-only policy grounding: PASS. Frontend only displays backend output and citations; no client-side policy generation.
3. Secure tooling/schema contracts: PASS. Tool-call rendering uses typed schemas mirroring existing backend contracts.
4. Privacy by default: PASS. Frontend does not bypass backend redaction pipeline and avoids raw payload dumping for errors.
5. Prompt injection resistance/fail-safe outcomes: PASS. Blocked responses are displayed through explicit safe error UI.
6. Stateful orchestration/contracts: PASS. Client honors SSE event contract and preserves event ordering in UI state.
7. End-to-end verification: PASS with manual walkthrough criteria across all existing stages.
8. Honest Copilot documentation: PASS as process requirement.

Post-Phase 1 design re-check:
All constitution gates remain PASS for the frontend-only scope.

## Project Structure

### Documentation (this feature)

```text
specs/013-react-frontend-chat/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── frontend-stream-contract.md
└── tasks.md
```

### Source Code (repository root)

```text
frontend/
├── index.html
├── package.json
├── tsconfig.json
├── vite.config.ts
├── postcss.config.js
├── tailwind.config.ts
└── src/
    ├── api/
    │   └── chatStream.ts
    ├── types/
    │   ├── events.ts
    │   └── toolPayloads.ts
    ├── components/
    │   ├── ChatView.tsx
    │   ├── MessageBubble.tsx
    │   ├── TicketStatusCard.tsx
    │   ├── PasswordResetCard.tsx
    │   └── TicketCreateCard.tsx
    ├── App.tsx
    ├── main.tsx
    └── index.css

src/
├── api/
├── agent/
└── ...

tests/
└── contract/
```

**Structure Decision**: Introduce a dedicated top-level `frontend/` app while preserving current backend project layout untouched; this cleanly isolates UI concerns and allows independent frontend build lifecycle.

## Complexity Tracking

No constitution violations requiring exception records.
