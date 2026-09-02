# Tasks: React Frontend Chat Experience

**Input**: Design documents from /specs/013-react-frontend-chat/

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/frontend-stream-contract.md

**Tests**: No additional frontend test framework setup is included for this pass; verification is manual walkthrough based.

**Organization**: Tasks are grouped by user story so each story can be implemented and validated independently.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Scaffold frontend application and baseline styling pipeline.

- [X] T001 Scaffold Vite React TypeScript app in frontend/ with baseline files frontend/package.json, frontend/vite.config.ts, frontend/tsconfig.json, and frontend/src/main.tsx
- [X] T002 Install and configure TailwindCSS with PostCSS in frontend/package.json, frontend/tailwind.config.ts, and frontend/postcss.config.js
- [X] T003 Wire Tailwind directives and base styles in frontend/src/index.css and ensure import in frontend/src/main.tsx

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Build typed contracts and streaming client primitives required by all stories.

**CRITICAL**: User story work starts only after this phase is complete.

- [X] T004 Create stream event interfaces mirroring backend schema in frontend/src/types/events.ts
- [X] T005 Create tool payload interfaces mirroring backend schemas in frontend/src/types/toolPayloads.ts
- [X] T006 Implement POST chat stream client with ReadableStream data-line parsing in frontend/src/api/chatStream.ts
- [X] T007 Implement safe parser helpers for tool_call and error payload JSON in frontend/src/api/chatStream.ts
- [X] T008 [P] Add shared frontend message and card model types in frontend/src/types/chatUi.ts

**Checkpoint**: Typed frontend contracts and streaming parser are ready.

---

## Phase 3: User Story 1 - Streamed Chat Interaction (Priority: P1) MVP

**Goal**: Users can send messages, see immediate local echo, and watch assistant tokens stream live until done.

**Independent Test**: Submit a valid message and confirm immediate user bubble, streamed assistant tokens, and done-driven loading completion.

### Implementation for User Story 1

- [X] T009 [P] [US1] Create generic message bubble component with user, assistant, and error variants in frontend/src/components/MessageBubble.tsx
- [X] T010 [US1] Create chat view component with input, send button, scrolling message list, and loading indicator in frontend/src/components/ChatView.tsx
- [X] T011 [US1] Implement App state for conversation timeline and pending assistant message lifecycle in frontend/src/App.tsx
- [X] T012 [US1] Wire send handler to append user message immediately and consume token events from chat stream client in frontend/src/App.tsx
- [X] T013 [US1] Handle done event to finalize assistant message and re-enable input/loading state in frontend/src/App.tsx

**Checkpoint**: Core streaming chat workflow works end-to-end for non-tool responses.

---

## Phase 4: User Story 2 - Structured Action Results and Safe Error Display (Priority: P1)

**Goal**: Tool responses render as structured cards and errors render safely without raw payload output.

**Independent Test**: Trigger each tool path and a blocked/error path to verify card rendering and safe error bubble behavior.

### Implementation for User Story 2

- [X] T014 [P] [US2] Create ticket status card component in frontend/src/components/TicketStatusCard.tsx
- [X] T015 [P] [US2] Create password reset card component in frontend/src/components/PasswordResetCard.tsx
- [X] T016 [P] [US2] Create ticket creation card component in frontend/src/components/TicketCreateCard.tsx
- [X] T017 [US2] Render tool_call payloads as typed cards and attach them to the active assistant response flow in frontend/src/App.tsx
- [X] T018 [US2] Log intent events to browser console without rendering intent messages in frontend/src/App.tsx
- [X] T019 [US2] Render backend error events and fetch-level failures through one safe error-display path in frontend/src/App.tsx and frontend/src/components/MessageBubble.tsx

**Checkpoint**: Tool and error events display in structured, user-safe form.

---

## Phase 5: User Story 3 - Session-Scoped Frontend Continuity (Priority: P2)

**Goal**: Stable per-page user/session identity and usable conversation continuity in current browser session.

**Independent Test**: Reload page to create fresh IDs, then send multiple messages to confirm stable IDs per page load and ordered conversation history.

### Implementation for User Story 3

- [X] T020 [US3] Generate user_id and session_id with crypto.randomUUID on app mount and keep them in component state in frontend/src/App.tsx
- [X] T021 [US3] Include generated user_id and session_id in every POST body to /chat/stream in frontend/src/App.tsx
- [X] T022 [US3] Enforce whitespace-only input prevention and graceful handling of backend validation errors in frontend/src/App.tsx and frontend/src/components/ChatView.tsx
- [X] T023 [US3] Keep chronological in-session conversation rendering with auto-scroll updates in frontend/src/components/ChatView.tsx

**Checkpoint**: Current-session continuity and input-safety behavior are complete.

---

## Phase 6: Polish and Cross-Cutting Concerns

**Purpose**: Final integration checks and manual validation documentation.

- [X] T024 [P] Document frontend run steps and manual verification scenarios in specs/013-react-frontend-chat/quickstart.md
- [X] T025 Run production build verification command for frontend in frontend/package.json via npm run build
- [X] T026 Record manual walkthrough outcomes for stream, tool cards, policy citations, and blocked error display in specs/013-react-frontend-chat/quickstart.md

---

## Dependencies and Execution Order

### Phase Dependencies

- Phase 1: no dependencies.
- Phase 2: depends on Phase 1 and blocks all story phases.
- Phase 3: depends on Phase 2.
- Phase 4: depends on Phase 2 and integrates with US1 chat flow.
- Phase 5: depends on Phase 2 and final App wiring from US1.
- Phase 6: depends on all user stories being complete.

### User Story Dependencies

- US1: can start once foundational stream/types work is complete.
- US2: depends on foundational types and stream parser; integrates with US1 assistant rendering path.
- US3: depends on foundational stream client and App state flow from US1.

### Within Each User Story

- Build components and types before integrating App wiring that consumes them.
- Complete event-handling logic before final manual walkthrough updates.

---

## Parallel Opportunities

- T008 can run in parallel with T006 and T007.
- T009 can run in parallel with T010.
- T014, T015, and T016 can run in parallel.
- T024 can run in parallel with T025 once implementation is stable.

## Parallel Example: User Story 1

- T009 Create frontend/src/components/MessageBubble.tsx
- T010 Create frontend/src/components/ChatView.tsx

## Parallel Example: User Story 2

- T014 Create frontend/src/components/TicketStatusCard.tsx
- T015 Create frontend/src/components/PasswordResetCard.tsx
- T016 Create frontend/src/components/TicketCreateCard.tsx

## Parallel Example: User Story 3

- T022 Input validation and backend validation fallback in frontend/src/App.tsx and frontend/src/components/ChatView.tsx
- T023 Conversation ordering and auto-scroll in frontend/src/components/ChatView.tsx

---

## Implementation Strategy

### MVP First (User Story 1)

1. Complete Setup and Foundational phases.
2. Complete US1 streaming chat flow.
3. Validate immediate echo, token streaming, and done-state completion.

### Incremental Delivery

1. Add US1 for usable core chat.
2. Add US2 for structured tool-card and safe error UX.
3. Add US3 for stable session identity and continuity.
4. Complete polish with build verification and manual walkthrough notes.

### Scope Guardrails

- No tasks include backend changes or new endpoints.
- No tasks include auth, health polling/gating logic, cross-session history browsing, or long-term memory display.

---

## Notes

- Checklist format is enforced for all tasks.
- File paths reference the frontend scope only plus feature docs for walkthrough evidence.
