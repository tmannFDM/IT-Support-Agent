# Tasks: FastMCP Ticket Status Slice

**Input**: Design documents from /specs/004-fastmcp-ticket-status/

**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Contract tests are included because acceptance criteria explicitly require stream-sequence and regression verification.

**Organization**: Tasks are grouped by user story so each story can be implemented and validated independently.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Add dependencies and file scaffolding for the ticket-status vertical slice.

- [X] T001 Add FastMCP dependency for tool runtime in requirements.txt
- [X] T002 Create tools package initialization in src/tools/__init__.py
- [X] T003 Create ticket-status tool module skeleton in src/tools/ticket_status_tool.py

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Build shared contracts and tool infrastructure required by all user stories.

**CRITICAL**: No user story work starts until this phase is complete.

- [X] T004 [P] Implement TicketStatusRequest and TicketStatusResponse models in src/schemas/ticket_status.py
- [X] T005 [P] Implement mocked in-memory ticket store with TKT-#### samples and UTC Z timestamps in src/tools/ticket_store.py
- [X] T006 Implement FastMCP ticket_status_lookup tool with Pydantic input/output validation in src/tools/ticket_status_tool.py
- [X] T007 [P] Extend agent state for ticket-status fields in src/agent/state.py
- [X] T008 Add ticket ID extraction helper using case-insensitive TKT-\d+ matching in src/agent/nodes.py

**Checkpoint**: Tool contracts and shared lookup infrastructure are ready.

---

## Phase 3: User Story 1 - Retrieve Ticket Status via Tool (Priority: P1) MVP

**Goal**: Return real ticket status results with intent, tool_call payload, summary token, and done events.

**Independent Test**: Send ticket-status requests with known and unknown IDs and verify required stream sequence and event types.

### Tests for User Story 1

- [X] T009 [P] [US1] Add contract test for valid ticket ID sequence intent -> tool_call -> token -> done in tests/contract/test_chat_stream.py
- [X] T010 [P] [US1] Add contract test for unknown well-formed ticket ID returning not-found token and done without error in tests/contract/test_chat_stream.py

### Implementation for User Story 1

- [X] T011 [US1] Implement check_ticket_status node success and not-found paths in src/agent/nodes.py
- [X] T012 [US1] Route ticket-status action_request messages from classify flow to check_ticket_status path in src/agent/graph.py
- [X] T013 [US1] Keep non-ticket action_request messages on placeholder path in src/agent/nodes.py
- [X] T014 [US1] Emit tool_call event with JSON-serialized TicketStatusResponse string data in src/api/routes/chat.py
- [X] T015 [US1] Emit natural-language token summary after tool_call for successful ticket lookups in src/api/routes/chat.py

**Checkpoint**: Ticket-status lookup behavior is functional and independently testable.

---

## Phase 4: User Story 2 - Handle Missing Ticket ID Safely (Priority: P1)

**Goal**: Return a user-correctable error when ticket-status request lacks an identifiable ticket ID, without calling the tool.

**Independent Test**: Send ticket-status request without TKT ID and verify stream emits intent then error only, with no tool_call and no done.

### Tests for User Story 2

- [X] T016 [P] [US2] Add contract test for missing ticket ID returning intent then error without tool_call or done in tests/contract/test_chat_stream.py

### Implementation for User Story 2

- [X] T017 [US2] Implement missing-ticket-ID branch that skips tool invocation in src/agent/nodes.py
- [X] T018 [US2] Return explicit missing-ID error state from check_ticket_status node for route-level error streaming in src/agent/nodes.py

**Checkpoint**: Missing-ID behavior is safe, deterministic, and independently testable.

---

## Phase 5: User Story 3 - Preserve Existing Behavior for Other Requests (Priority: P2)

**Goal**: Keep stage-1 and stage-2 behavior unchanged except for targeted ticket-status routing.

**Independent Test**: Re-run existing validation and disconnect tests plus non-ticket action_request path checks.

### Tests for User Story 3

- [X] T019 [P] [US3] Add regression assertion that non-ticket action_request still returns existing placeholder sequence in tests/contract/test_chat_stream.py
- [X] T020 [P] [US3] Add regression assertion that stage-1 validation error shape remains unchanged in tests/contract/test_chat_stream.py
- [X] T021 [P] [US3] Add regression assertion that disconnect handling remains immediate stop with no post-disconnect events in tests/contract/test_chat_stream.py

### Implementation for User Story 3

- [X] T022 [US3] Restrict ticket-status routing guards so direct_response and non-ticket flows remain unchanged in src/agent/nodes.py
- [X] T023 [US3] Preserve existing validation and disconnect control flow while adding tool_call handling in src/api/routes/chat.py

**Checkpoint**: Prior slice behavior remains intact while ticket-status routing is enabled.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Finalize docs and verification evidence for this scope.

- [X] T024 [P] Update ticket-status quickstart scenarios and expected event sequences in specs/004-fastmcp-ticket-status/quickstart.md
- [X] T025 [P] Update contract examples for JSON-serialized tool_call payload data in specs/004-fastmcp-ticket-status/contracts/http-api.md
- [X] T026 Run full test suite and record verification notes in specs/004-fastmcp-ticket-status/quickstart.md

---

## Dependencies & Execution Order

### Phase Dependencies

- Setup (Phase 1): no dependencies.
- Foundational (Phase 2): depends on Setup completion and blocks all user stories.
- User Story phases (Phase 3-5): depend on Foundational completion.
- Polish (Phase 6): depends on completed user stories.

### User Story Dependencies

- User Story 1 (P1): starts after Foundational completion.
- User Story 2 (P1): starts after User Story 1 establishes check_ticket_status node baseline.
- User Story 3 (P2): starts after User Story 1 and User Story 2 integration to validate regressions.

### Within Each User Story

- Write contract tests first and verify they fail before implementation.
- Implement node and routing logic before final stream-sequence checks.
- Complete each story checkpoint before moving to the next story.

### Parallel Opportunities

- T004 and T005 can run in parallel.
- T009 and T010 can run in parallel.
- T019, T020, and T021 can run in parallel.
- T024 and T025 can run in parallel.

---

## Parallel Example: User Story 1

- Task T009 in tests/contract/test_chat_stream.py
- Task T010 in tests/contract/test_chat_stream.py

## Parallel Example: User Story 3

- Task T019 in tests/contract/test_chat_stream.py
- Task T020 in tests/contract/test_chat_stream.py
- Task T021 in tests/contract/test_chat_stream.py

---

## Implementation Strategy

### MVP First (User Story 1)

1. Complete Phase 1 Setup.
2. Complete Phase 2 Foundational tasks.
3. Complete Phase 3 User Story 1.
4. Validate User Story 1 independently before moving on.

### Incremental Delivery

1. Add missing-ID safety path in User Story 2.
2. Add regression-preservation guarantees in User Story 3.
3. Complete documentation and full-suite verification in Phase 6.

### Scope Guardrails

- Do not add tasks for RAG/ChromaDB, password reset or ticket creation tools, PII redaction, prompt injection detection, long-term memory, Phoenix instrumentation, Promptfoo, or React frontend.
- Do not add tasks that modify stage-1 validation/error/disconnect behavior.
- Do not broaden stage-2 intent and direct_response behavior beyond routing ticket-status action_request messages to check_ticket_status.
