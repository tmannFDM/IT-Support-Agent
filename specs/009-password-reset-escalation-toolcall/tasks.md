# Tasks: Password Reset Escalation ToolCall Fix

**Input**: Design documents from /specs/009-password-reset-escalation-toolcall/

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/http-api.md, quickstart.md

**Tests**: Contract tests are required because this is a stream-order and payload-structure bug fix.

**Organization**: Tasks are grouped by user story to keep each fix slice independently testable.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Confirm strict bug-fix scope and target files.

- [X] T001 Confirm implementation scope is limited to src/agent/nodes.py, src/api/routes/chat.py (if needed), and tests/contract/test_chat_stream.py

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Verify existing escalation and tool_call pathways before modifying behavior.

**CRITICAL**: No user story work starts until this phase is complete.

- [X] T002 Verify escalation-path currently emits token content and identify raw field-name leak source in src/agent/nodes.py
- [X] T003 Verify stream emitter already supports tool_call emission ordering requirements in src/api/routes/chat.py

**Checkpoint**: Bug source and required fix surfaces are confirmed.

---

## Phase 3: User Story 1 - Structured Escalation Metadata in Stream (Priority: P1)

**Goal**: Emit full escalated PasswordResetResponse as tool_call data before token on escalation paths.

**Independent Test**: Escalated requests emit intent, tool_call with status escalated and correct escalation_reason, then token, then done.

### Implementation for User Story 1

- [X] T004 [US1] Update check_password_reset escalation path to populate tool_call with JSON-serialized full PasswordResetResponse payload in src/agent/nodes.py
- [X] T005 [US1] Ensure escalation path preserves intent -> tool_call -> token -> done ordering via existing stream logic in src/api/routes/chat.py

**Checkpoint**: Escalation structured data is carried in tool_call event before token.

---

## Phase 4: User Story 2 - Clean Human-Readable Escalation Token (Priority: P1)

**Goal**: Remove raw key leakage from escalation token output while keeping explanatory wording.

**Independent Test**: Escalation token text contains only human-readable message and no raw field-name fragments.

### Implementation for User Story 2

- [X] T006 [US2] Replace escalation token composition to remove key=value and field-name fragments while preserving user-facing escalation explanation in src/agent/nodes.py

**Checkpoint**: Escalation token no longer leaks internal field identifiers.

---

## Phase 5: User Story 3 - Preserve Existing Sequence and Prior Behavior (Priority: P2)

**Goal**: Update escalation contract assertions only, keeping success and prior-stage behavior unchanged.

**Independent Test**: Existing success password-reset test remains valid; three escalation tests now assert tool_call before token with correct escalation_reason.

### Tests for User Story 3

- [X] T007 [US3] Update invalid-ID escalation contract test to assert tool_call appears before token and payload escalation_reason is invalid_employee_id in tests/contract/test_chat_stream.py
- [X] T008 [US3] Update urgency-pressure escalation contract test to assert tool_call appears before token and payload escalation_reason is urgency_pressure in tests/contract/test_chat_stream.py
- [X] T009 [US3] Update vague-reason escalation contract test to assert tool_call appears before token and payload escalation_reason is vague_reason in tests/contract/test_chat_stream.py
- [X] T010 [US3] Run contract tests for password-reset scenarios in tests/contract/test_chat_stream.py
- [X] T011 [US3] Run full regression tests in tests to confirm no prior-stage behavior changes

**Checkpoint**: Bug-fix assertions pass and broader behavior remains stable.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final scope and behavior audit for this bug-fix slice.

- [X] T012 Confirm no changes outside escalation tool_call emission, token cleanup, and three escalation test assertions in specs/009-password-reset-escalation-toolcall/quickstart.md

---

## Dependencies & Execution Order

### Phase Dependencies

- Phase 1: no dependencies.
- Phase 2: depends on Phase 1 and blocks user stories.
- Phase 3: depends on Phase 2.
- Phase 4: depends on Phase 3.
- Phase 5: depends on Phases 3 and 4.
- Phase 6: depends on all prior phases.

### User Story Dependencies

- US1 (P1): first bug-fix increment.
- US2 (P1): applies token cleanup after structured tool_call emission is in place.
- US3 (P2): validates regression safety and updated escalation assertions.

### Within Each User Story

- Implement behavior updates in node/stream files.
- Update test assertions for affected escalation scenarios.
- Run contract then full regression suites.

### Parallel Opportunities

- T007, T008, and T009 can be authored in parallel in tests/contract/test_chat_stream.py, then merged sequentially.
- T010 and T012 can run in parallel after implementation is complete.

---

## Parallel Example: Escalation Tests

- T007 in tests/contract/test_chat_stream.py
- T008 in tests/contract/test_chat_stream.py
- T009 in tests/contract/test_chat_stream.py

---

## Implementation Strategy

### MVP First (US1)

1. Confirm scope and current leak source.
2. Emit structured escalation tool_call before token.
3. Verify event ordering is correct.

### Incremental Delivery

1. Deliver structured escalation tool_call output.
2. Remove token text leakage.
3. Update three escalation tests and run regressions.

### Scope Guardrails

- Include only escalation tool_call emission fix, token leak removal, and three escalation test assertion updates.
- Exclude any schema changes, success-path behavior changes, or unrelated stage/tool modifications.
