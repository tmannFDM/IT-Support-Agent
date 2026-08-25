# Tasks: Chat Error Handling Baseline

**Input**: Design documents from /specs/002-chat-error-handling/

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/http-api.md

**Tests**: Contract tests are included because acceptance criteria explicitly require API behavior checks for /chat/stream and /health.

**Organization**: Tasks are grouped by user story for independent implementation and validation.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Bootstrap minimal FastAPI project skeleton and testing baseline for this pass

- [X] T001 Create package initialization files in src/api/__init__.py and src/schemas/__init__.py
- [X] T002 Define runtime and test dependencies in requirements.txt
- [X] T003 Create FastAPI application entrypoint and router wiring scaffold in src/api/main.py

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Shared contracts and helpers required before story implementation

**CRITICAL**: No user story implementation begins until this phase is complete

- [X] T004 [P] Implement ChatRequest and ChatStreamEvent schema contracts in src/schemas/chat.py
- [X] T005 [P] Implement validation error response schemas for error_code, message, and details items in src/schemas/errors.py
- [X] T006 Implement validation exception mapping to HTTP 422 and ERR-VALIDATION-MISSING-FIELD in src/api/errors.py
- [X] T007 Implement SSE event encoding helper for chat stream events in src/api/sse.py
- [X] T008 Register shared error handlers and route includes in src/api/main.py

**Checkpoint**: Foundation complete and user-story tasks can proceed

---

## Phase 3: User Story 1 - Validate Required Chat Inputs (Priority: P1) MVP

**Goal**: Enforce deterministic validation for missing, empty, and whitespace-only required fields

**Independent Test**: POST /chat/stream with invalid required fields returns HTTP 422 with error_code, message, and all-invalid-field details structure

### Tests for User Story 1

- [X] T009 [US1] Add contract tests for missing and empty required fields on /chat/stream in tests/contract/test_chat_stream.py
- [X] T010 [US1] Add contract tests for whitespace-only fields and trim-then-validate behavior on /chat/stream in tests/contract/test_chat_stream.py
- [X] T011 [US1] Add contract test asserting details includes all invalid required fields with field/issue shape in tests/contract/test_chat_stream.py

### Implementation for User Story 1

- [X] T012 [US1] Implement request normalization and required-field validation flow in src/api/routes/chat.py
- [X] T013 [US1] Implement validation error payload assembly with stable keys error_code and message in src/api/errors.py
- [X] T014 [US1] Implement full invalid-field details population using field and issue entries in src/api/errors.py

**Checkpoint**: User Story 1 independently passes validation contract scenarios

---

## Phase 4: User Story 2 - Stop Work on Stream Disconnect (Priority: P1)

**Goal**: Stop generation immediately on client disconnect with no retry and no further events

**Independent Test**: Start /chat/stream, disconnect client mid-stream, and verify generation stop semantics

### Tests for User Story 2

- [X] T015 [US2] Add contract-level disconnect handling test for /chat/stream stream cancellation behavior in tests/contract/test_chat_stream.py

### Implementation for User Story 2

- [X] T016 [US2] Implement disconnect detection and immediate generation stop in src/api/routes/chat.py
- [X] T017 [US2] Enforce no-retry and no-further-events behavior after disconnect in src/api/routes/chat.py

**Checkpoint**: User Story 2 independently enforces disconnect lifecycle behavior

---

## Phase 5: User Story 3 - Keep Error Scope Explicit for This Pass (Priority: P2)

**Goal**: Keep this pass constrained to defined validation and disconnect errors only

**Independent Test**: Review API contract and quickstart docs to confirm no additional error-code requirements are introduced

### Tests for User Story 3

- [X] T018 [US3] Add contract assertion that validation failures for this pass use ERR-VALIDATION-MISSING-FIELD only in tests/contract/test_chat_stream.py

### Implementation for User Story 3

- [X] T019 [US3] Document explicit out-of-scope error-code domains in specs/002-chat-error-handling/contracts/http-api.md
- [X] T020 [US3] Align quickstart error-handling expectations with scoped contract behavior in specs/002-chat-error-handling/quickstart.md

**Checkpoint**: User Story 3 preserves scope boundaries for current delivery

---

## Phase 6: Polish and Cross-Cutting Concerns

**Purpose**: Final verification and baseline documentation updates

- [X] T021 [P] Add API usage examples for /chat/stream and /health in README.md
- [X] T022 Run quickstart verification steps and record expected outcomes consistency in specs/002-chat-error-handling/quickstart.md

---

## Dependencies and Execution Order

### Phase Dependencies

- Setup (Phase 1): starts immediately
- Foundational (Phase 2): depends on Setup and blocks all stories
- User Stories (Phases 3-5): depend on Foundational completion
- Polish (Phase 6): depends on completion of targeted user stories

### User Story Dependencies

- User Story 1: depends on Foundational only
- User Story 2: depends on Foundational and reuses /chat/stream baseline from User Story 1
- User Story 3: depends on Foundational and contract baseline from User Story 1

### Within Each User Story

- Write story tests first and confirm they fail before implementation
- Implement route and validation behavior after schema contracts are in place
- Confirm independent story checkpoint before proceeding

### Parallel Opportunities

- T004 and T005 can execute in parallel
- T009, T010, and T011 can execute in parallel by splitting test cases
- T019 and T020 can execute in parallel
- T021 can execute in parallel with T022

---

## Parallel Example: User Story 1

```bash
Task T009: Add missing and empty field tests in tests/contract/test_chat_stream.py
Task T010: Add whitespace-only field tests in tests/contract/test_chat_stream.py
Task T011: Add all-invalid-fields details shape test in tests/contract/test_chat_stream.py
```

## Parallel Example: User Story 3

```bash
Task T019: Update scoped error-code contract docs in specs/002-chat-error-handling/contracts/http-api.md
Task T020: Update scoped quickstart expectations in specs/002-chat-error-handling/quickstart.md
```

---

## Implementation Strategy

### MVP First

1. Complete Phase 1 and Phase 2
2. Complete User Story 1 and validate 422 error contract behavior
3. Complete User Story 2 and validate disconnect handling

### Incremental Delivery

1. Deliver validation contract behavior (US1)
2. Add disconnect stop semantics (US2)
3. Lock scoped error-domain documentation (US3)
4. Complete polish checks

### Scope Guardrails

- Do not add tasks for RAG, agent orchestration, tool execution, security middleware, evaluation, or frontend
- Keep implementation changes within src/api, src/schemas, tests, and existing feature documentation files
