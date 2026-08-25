# Tasks: Chat Stream Vertical Slice

**Input**: Design documents from `/specs/001-chat-stream-slice/`

**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Contract tests are included because acceptance criteria explicitly require validating `/chat/stream` and `/health` behavior.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Initialize a runnable FastAPI project baseline for this slice

- [ ] T001 Create package initialization files in src/api/__init__.py and src/schemas/__init__.py
- [ ] T002 Define runtime and test dependencies in requirements.txt
- [ ] T003 Create FastAPI app bootstrap and router inclusion points in src/api/main.py

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core contracts and shared utilities that block user stories

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T004 [P] Implement shared SSE event serialization helper in src/api/sse.py
- [ ] T005 [P] Define validation error response schema for API boundaries in src/schemas/errors.py
- [ ] T006 Implement global request validation exception mapping with error code ERR-VALIDATION-MISSING-FIELD in src/api/errors.py
- [ ] T007 Wire exception handlers and route registration in src/api/main.py

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Stream Basic Chat Response (Priority: P1) 🎯 MVP

**Goal**: Accept a valid ChatRequest and stream deterministic SSE response ending with done

**Independent Test**: Send valid POST `/chat/stream` payload and verify stream emits token event(s) then one done event

### Tests for User Story 1

- [ ] T008 [US1] Add contract test for successful `/chat/stream` SSE flow in tests/contract/test_chat_stream.py

### Implementation for User Story 1

- [ ] T009 [P] [US1] Implement ChatRequest and ChatStreamEvent schemas in src/schemas/chat.py
- [ ] T010 [P] [US1] Add reserved forward-compatibility schemas ToolCallCard, TicketStatusResponse, PasswordResetRequest, and TicketCreateRequest in src/schemas/support.py
- [ ] T011 [US1] Implement `/chat/stream` route with hardcoded or echoed streaming response in src/api/routes/chat.py
- [ ] T012 [US1] Register chat router in src/api/main.py

**Checkpoint**: User Story 1 is independently functional and stream-complete

---

## Phase 4: User Story 2 - Reject Invalid Chat Requests (Priority: P1)

**Goal**: Return clear validation failures with ERR-VALIDATION-MISSING-FIELD for missing or empty required fields

**Independent Test**: Submit missing-field and empty-string payloads and verify error code and clear message

### Tests for User Story 2

- [ ] T013 [US2] Add contract tests for missing required fields on `/chat/stream` in tests/contract/test_chat_stream.py
- [ ] T014 [US2] Add contract tests for empty required fields on `/chat/stream` in tests/contract/test_chat_stream.py

### Implementation for User Story 2

- [ ] T015 [US2] Enforce empty-string validation semantics for required chat fields in src/schemas/chat.py
- [ ] T016 [US2] Normalize validation error payloads to include ERR-VALIDATION-MISSING-FIELD in src/api/errors.py

**Checkpoint**: User Story 2 returns consistent boundary validation errors independently

---

## Phase 5: User Story 3 - Verify Service Readiness (Priority: P2)

**Goal**: Provide a health endpoint proving service readiness and version visibility

**Independent Test**: Call GET `/health` and verify HTTP 200 with non-empty status and version values

### Tests for User Story 3

- [ ] T017 [US3] Add contract test for GET `/health` success response in tests/contract/test_health.py

### Implementation for User Story 3

- [ ] T018 [US3] Implement `/health` route returning service status and version in src/api/routes/health.py
- [ ] T019 [US3] Register health router in src/api/main.py

**Checkpoint**: User Story 3 is independently functional and verifiable

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final consistency checks for this scoped slice

- [ ] T020 [P] Add usage examples for `/chat/stream` and `/health` in README.md
- [ ] T021 Run quickstart validation steps and align expected outcomes in specs/001-chat-stream-slice/quickstart.md

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3+)**: Depend on Foundational completion
- **Polish (Phase 6)**: Depends on all targeted stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Starts after Phase 2, no dependency on other stories
- **User Story 2 (P1)**: Starts after Phase 2, depends on US1 route and schema baseline
- **User Story 3 (P2)**: Starts after Phase 2, independent of US1/US2 logic

### Within Each User Story

- Tests are written before implementation and should fail before code changes
- Schemas before route logic
- Route logic before app wiring
- Story checkpoint must pass before moving on

### Parallel Opportunities

- **Setup**: none
- **Foundational**: T004 and T005 can run in parallel
- **US1**: T009 and T010 can run in parallel
- **US2**: T013 and T014 can run in parallel
- **US3**: T017 can run while T018 is in progress if different developers are available
- **Polish**: T020 and T021 can run in parallel

---

## Parallel Example: User Story 1

```bash
Task T009: Implement ChatRequest and ChatStreamEvent schemas in src/schemas/chat.py
Task T010: Add reserved forward-compatibility schemas in src/schemas/support.py
```

## Parallel Example: User Story 2

```bash
Task T013: Add contract tests for missing required fields in tests/contract/test_chat_stream.py
Task T014: Add contract tests for empty required fields in tests/contract/test_chat_stream.py
```

## Parallel Example: User Story 3

```bash
Task T017: Add contract test for GET /health in tests/contract/test_health.py
Task T018: Implement /health route in src/api/routes/health.py
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational
3. Complete Phase 3: User Story 1
4. Validate stream behavior end-to-end with contract tests

### Incremental Delivery

1. Deliver US1 as MVP vertical slice
2. Add US2 to harden boundary validation semantics
3. Add US3 for operational readiness checks
4. Complete Polish phase documentation and quickstart validation

### Scope Guardrails

- Do not add tasks for RAG, agent orchestration, tool execution, security middleware, evaluation pipelines, or frontend work in this pass
- Keep all implementation in src/api/, src/schemas/, and tests/
