# Tasks: Ticket Creation Tool Slice

**Input**: Design documents from `/specs/010-ticket-creation-tool-slice/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/http-api.md

**Tests**: Contract tests are required for this slice per specification and user request.

**Organization**: Tasks are grouped by user story so each story can be implemented and validated independently.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Add minimal shared scaffolding for new ticket-creation schema/tool integration.

- [X] T001 Create shared in-memory ticket store module scaffold in src/tools/ticket_store.py
- [X] T002 [P] Create ticket creation schema module scaffold in src/schemas/ticket_create.py
- [X] T003 [P] Add module exports for new ticket artifacts in src/tools/__init__.py and src/schemas/__init__.py

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Implement deterministic store and routing primitives required by all user stories.

**⚠️ CRITICAL**: No user story work should begin until this phase is complete.

- [X] T004 Implement shared ticket store accessors (read/add/list IDs) in src/tools/ticket_store.py
- [X] T005 Implement next ticket ID generation with collision-scan increment above seeded TKT-1001 range in src/tools/ticket_store.py
- [X] T006 Add ticket-creation state fields needed for tool_call/error routing in src/agent/state.py
- [X] T007 Add ticket ID pattern helper and ticket-creation intent phrase constants in src/agent/nodes.py

**Checkpoint**: Foundation ready - story implementation can proceed.

---

## Phase 3: User Story 1 - Create IT Ticket from Action Request (Priority: P1) 🎯 MVP

**Goal**: Replace placeholder action-request behavior with successful schema-validated ticket creation flow.

**Independent Test**: Submit a clear ticket-creation request and verify `intent -> tool_call -> token -> done` with valid TicketCreateResponse payload.

### Tests for User Story 1

- [X] T008 [P] [US1] Add contract test for successful categorizable ticket creation payload/order in tests/contract/test_chat_stream.py
- [X] T009 [P] [US1] Add contract test for default medium priority when no severity keywords are present in tests/contract/test_chat_stream.py

### Implementation for User Story 1

- [X] T010 [P] [US1] Implement TicketCreateRequest and TicketCreateResponse Literal-constrained models in src/schemas/ticket_create.py
- [X] T011 [US1] Implement create_ticket FastMCP tool using TicketCreateRequest/Response and shared store writes in src/tools/create_ticket.py
- [X] T012 [US1] Wire create_ticket schema/tool exports in src/schemas/__init__.py and src/tools/__init__.py
- [X] T013 [US1] Implement category keyword detection with fixed precedence Access > VPN > Password > Hardware > Software in src/agent/nodes.py
- [X] T014 [US1] Implement priority keyword detection with medium default in src/agent/nodes.py
- [X] T015 [US1] Implement create_ticket_node success path producing TicketCreateResponse tool_call and confirmation token in src/agent/nodes.py
- [X] T016 [US1] Route ticket-creation action requests to create_ticket_node in src/agent/graph.py

**Checkpoint**: User Story 1 independently supports successful ticket creation.

---

## Phase 4: User Story 2 - Fail Safe for Uncategorizable Requests (Priority: P1)

**Goal**: Prevent guessed ticket creation when category keywords are missing.

**Independent Test**: Submit a vague create request and verify error event is returned with no ticket created.

### Tests for User Story 2

- [X] T017 [P] [US2] Add contract test for vague uncategorizable create request returning error without tool_call in tests/contract/test_chat_stream.py

### Implementation for User Story 2

- [X] T018 [US2] Add uncategorizable description guard that returns error and skips store writes in src/agent/nodes.py

**Checkpoint**: User Story 2 independently enforces fail-safe behavior.

---

## Phase 5: User Story 3 - New Ticket Immediately Lookupable and Mixed-Intent Safe Routing (Priority: P2)

**Goal**: Ensure created IDs are immediately status-lookupable and valid ticket-ID references take routing precedence.

**Independent Test**: Create ticket, then lookup same ID successfully; verify mixed message with valid ID routes to status lookup instead of create.

### Tests for User Story 3

- [X] T019 [P] [US3] Add contract test that newly created ticket_id is immediately retrievable via existing status lookup path in tests/contract/test_chat_stream.py
- [X] T020 [P] [US3] Add contract test that mixed create/status message with valid ticket ID routes to status lookup in tests/contract/test_chat_stream.py

### Implementation for User Story 3

- [X] T021 [US3] Integrate shared ticket store access with existing status lookup read path without changing lookup logic in src/tools/ticket_store.py
- [X] T022 [US3] Implement mixed-intent precedence check for valid ticket ID before creation cues in src/agent/nodes.py and src/agent/graph.py

**Checkpoint**: User Story 3 independently verifies shared-store consistency and safe mixed-intent precedence.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Confirm no regressions and align feature docs with validated behavior.

- [X] T023 [P] Run contract regression for ticket creation and prior stream flows in tests/contract/test_chat_stream.py
- [X] T024 [P] Run full regression suite to confirm stage 1-6 behavior remains unchanged in tests/
- [X] T025 Update validation notes with executed commands/outcomes in specs/010-ticket-creation-tool-slice/quickstart.md

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies.
- **Phase 2 (Foundational)**: Depends on Phase 1 and blocks all user stories.
- **Phase 3 (US1)**: Depends on Phase 2.
- **Phase 4 (US2)**: Depends on Phase 2 and reuses US1 create_ticket_node logic.
- **Phase 5 (US3)**: Depends on Phase 2 and US1 create/store integration.
- **Phase 6 (Polish)**: Depends on completion of all targeted user stories.

### User Story Dependencies

- **US1 (P1)**: Starts immediately after foundational phase; MVP slice.
- **US2 (P1)**: Depends on US1 create node behavior for fail-safe branching.
- **US3 (P2)**: Depends on US1 store insertion path and foundational ticket-ID detection primitives.

### Within Each User Story

- Write story tests first and confirm they fail before implementation.
- Implement inference and schemas before node wiring where applicable.
- Complete story-specific routing and payload behavior before moving to next story.

### Parallel Opportunities

- T002 and T003 can run in parallel in setup.
- T008 and T009 can run in parallel for US1 tests.
- T010 can run in parallel with test drafting (T008/T009) before integration tasks.
- T019 and T020 can run in parallel for US3 tests.
- T023 and T024 can run in parallel when implementation is complete.

---

## Parallel Example: User Story 1

```bash
# Contract tests for US1 in parallel:
Task: "T008 Add contract test for successful categorizable ticket creation payload/order in tests/contract/test_chat_stream.py"
Task: "T009 Add contract test for default medium priority when no severity keywords are present in tests/contract/test_chat_stream.py"

# Implementation tasks that can overlap:
Task: "T010 Implement TicketCreateRequest and TicketCreateResponse Literal-constrained models in src/schemas/ticket_create.py"
Task: "T013 Implement category keyword detection with fixed precedence Access > VPN > Password > Hardware > Software in src/agent/nodes.py"
```

---

## Parallel Example: User Story 3

```bash
# Contract tests for US3 in parallel:
Task: "T019 Add contract test that newly created ticket_id is immediately retrievable via existing status lookup path in tests/contract/test_chat_stream.py"
Task: "T020 Add contract test that mixed create/status message with valid ticket ID routes to status lookup in tests/contract/test_chat_stream.py"
```

---

## Implementation Strategy

### MVP First (US1)

1. Complete Phase 1 and Phase 2.
2. Complete Phase 3 (US1).
3. Validate successful creation flow and contract ordering before expanding scope.

### Incremental Delivery

1. Ship US1 ticket creation success path.
2. Add US2 fail-safe uncategorizable error behavior.
3. Add US3 immediate lookup and mixed-intent precedence behavior.
4. Run phase-6 regressions to confirm stage 1-6 behavior remains intact.

### Scope Guardrails

- Exclude long-term memory, Arize Phoenix instrumentation, Promptfoo evaluation, and React frontend tasks.
- Avoid tasks that modify password-reset, RAG, or guardrail logic outside minimal routing/shared-store integration required for this slice.
