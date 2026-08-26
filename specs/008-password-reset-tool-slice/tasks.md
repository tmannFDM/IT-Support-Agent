# Tasks: Password Reset Tool Slice

**Input**: Design documents from /specs/008-password-reset-tool-slice/

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/http-api.md, quickstart.md

**Tests**: Contract tests are included because acceptance criteria explicitly require deterministic success/escalation stream outcomes and stage 1-5 regression safety.

**Organization**: Tasks are grouped by user story so each story is independently implementable and testable.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Confirm implementation boundaries and align target files to constrained scope.

- [X] T001 Confirm feature scope and target files are limited to password-reset implementation surfaces: src/tools/password_reset.py, src/tools/__init__.py, src/schemas/password_reset.py, src/schemas/__init__.py, src/agent/nodes.py, src/agent/graph.py, src/agent/state.py, src/api/routes/chat.py, and tests/contract/test_chat_stream.py

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Add shared contracts and tool foundation required by all password-reset stories.

**CRITICAL**: No user story work starts until this phase is complete.

- [X] T002 Create PasswordResetRequest and PasswordResetResponse models in src/schemas/password_reset.py
- [X] T003 [P] Export password reset schema models from src/schemas/__init__.py
- [X] T004 Create password_reset FastMCP tool with mocked in-memory reset_issued response and fixed temporary_password_note in src/tools/password_reset.py
- [X] T005 [P] Register password_reset tool module in src/tools/__init__.py

**Checkpoint**: Schema-validated tool contract exists and returns deterministic mocked success payload without exposing real passwords.

---

## Phase 3: User Story 1 - Complete Password Reset Flow (Priority: P1) MVP

**Goal**: Route password-reset-specific action requests to a dedicated node and emit success stream sequence intent -> tool_call -> token -> done.

**Independent Test**: Send a valid password-reset request (valid EMP-\d{4} ID and specific reason) and verify tool_call payload plus confirmation token and done.

### Tests for User Story 1

- [X] T006 [US1] Add contract test for valid password reset request returning intent, tool_call(reset_issued), token, done in tests/contract/test_chat_stream.py

### Implementation for User Story 1

- [X] T007 [US1] Add password-reset intent routing branch for action_request messages in src/agent/nodes.py
- [X] T008 [US1] Implement check_password_reset node success path calling password_reset tool and returning intent/tool_call/token/done-compatible state in src/agent/nodes.py
- [X] T009 [US1] Wire check_password_reset node path into graph routing for password-reset-specific action requests in src/agent/graph.py

**Checkpoint**: Valid password-reset requests use the new node and no longer follow the generic action_request placeholder path.

---

## Phase 4: User Story 2 - Fail-Safe Escalation for Suspicious Requests (Priority: P1)

**Goal**: Escalate suspicious requests without tool execution using deterministic reason selection and stream sequence intent -> token -> done.

**Independent Test**: Submit suspicious messages and verify token escalation with reasons: invalid_employee_id, urgency_pressure, vague_reason, including precedence behavior.

### Tests for User Story 2

- [X] T010 [US2] Add contract test ensuring invalid employee ID escalates with invalid_employee_id even when urgency/vague signals are also present in tests/contract/test_chat_stream.py
- [X] T011 [US2] Add contract test ensuring urgency-pressure language escalates with urgency_pressure when employee ID is valid in tests/contract/test_chat_stream.py
- [X] T012 [US2] Add contract test ensuring fixed-list vague reason escalates with vague_reason when employee ID is valid and urgency is absent in tests/contract/test_chat_stream.py

### Implementation for User Story 2

- [X] T013 [US2] Implement EMP-\d{4} employee_id validation and invalid_employee_id escalation signal in src/agent/nodes.py
- [X] T014 [US2] Implement normalized urgency-pressure keyword detection using stage-5-style normalization in src/agent/nodes.py
- [X] T015 [US2] Implement normalized fixed-list vague-reason detection for reset templates in src/agent/nodes.py
- [X] T016 [US2] Implement single-reason precedence invalid_employee_id > urgency_pressure > vague_reason and bypass tool call on suspicious requests in src/agent/nodes.py

**Checkpoint**: Suspicious password-reset requests escalate deterministically as expected non-error outcomes.

---

## Phase 5: User Story 3 - Preserve Existing Stages and Contracts (Priority: P2)

**Goal**: Keep ticket-status, RAG, and stage-5 guardrail behavior unchanged while introducing password-reset routing.

**Independent Test**: Run existing contract/regression suite and verify non-password flows remain unchanged.

### Tests for User Story 3

- [X] T017 [US3] Run contract suite to verify password-reset additions and unchanged non-password stream behavior in tests/contract/test_chat_stream.py
- [X] T018 [US3] Run full pytest suite to confirm stage 1-5 regressions remain passing in tests

### Implementation for User Story 3

- [X] T019 [US3] Verify routing changes do not alter ticket_status_lookup, RAG policy flow, or guardrail behavior outside password-reset branch in src/agent/nodes.py

**Checkpoint**: Existing stage 1-5 behavior remains intact with password-reset slice added.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final consistency and scope audit for this slice.

- [X] T020 Confirm no out-of-scope changes were introduced (ticket creation, long-term memory, Arize Phoenix, Promptfoo, React frontend) and no direct modifications to ticket_status_lookup, RAG pipeline, or guardrail logic beyond password-reset routing in specs/008-password-reset-tool-slice/quickstart.md

---

## Dependencies & Execution Order

### Phase Dependencies

- Phase 1 (Setup): no dependencies.
- Phase 2 (Foundational): depends on Phase 1 and blocks user stories.
- Phase 3 (US1): depends on Phase 2.
- Phase 4 (US2): depends on Phase 3 routing and node baseline.
- Phase 5 (US3): depends on Phases 3-4 completion.
- Phase 6 (Polish): depends on all prior phases.

### User Story Dependencies

- US1 (P1): first MVP increment.
- US2 (P1): extends US1 with suspicion and escalation logic.
- US3 (P2): validates no regression to existing stages.

### Within Each User Story

- Add tests for story criteria.
- Implement story logic.
- Run validations for story acceptance and regressions.

### Parallel Opportunities

- T003 and T005 can run in parallel (different files).
- T010, T011, and T012 can be authored in parallel within tests/contract/test_chat_stream.py, then merged sequentially.
- T017 and T019 can execute in parallel (validation command and code audit).

---

## Parallel Example: Foundational

- T003 in src/schemas/__init__.py
- T005 in src/tools/__init__.py

## Parallel Example: Suspicion Escalation Tests

- T010 in tests/contract/test_chat_stream.py
- T011 in tests/contract/test_chat_stream.py
- T012 in tests/contract/test_chat_stream.py

---

## Implementation Strategy

### MVP First (US1)

1. Complete Setup and Foundational phases.
2. Implement routing and node success path.
3. Validate valid password-reset stream behavior.

### Incremental Delivery

1. Deliver schema + tool contract.
2. Deliver success path routing.
3. Add suspicious escalation logic with precedence.
4. Run contract and full regression suites.

### Scope Guardrails

- Include only password_reset tool, password reset schemas, password-reset node/routing, and specified contract tests.
- Exclude ticket creation tooling, long-term memory, Arize Phoenix, Promptfoo, and React frontend.
- Do not modify ticket_status_lookup, RAG pipeline, or guardrail logic beyond password-reset branch routing.
