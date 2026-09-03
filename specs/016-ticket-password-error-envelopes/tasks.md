# Tasks: Ticket Password Error Envelopes (Feature 016)

**Input**: Design documents from `/specs/016-ticket-password-error-envelopes/`

**Prerequisites**: [plan.md](plan.md), [spec.md](spec.md), [research.md](research.md), [data-model.md](data-model.md), and [ticket-password-error-envelope.md](contracts/ticket-password-error-envelope.md)

**Scope**: Only the missing-category and tool-call exception branches in `create_ticket_node`, the tool-call exception branch in `check_password_reset_node`, and their corresponding assertions in the existing chat-stream contract tests. No other files or behaviors are in scope.

**Tests**: Existing pytest contract tests must be updated before implementation and then run. No new test harness, schema, routing, inference, or frontend work is included.

## Phase 1: Contract Test Preparation

**Purpose**: Specify the three corrected error-event payloads before changing the node outputs.

- [X] T001 [US1] Update the vague ticket-category error assertion in `tests/contract/test_chat_stream.py` to parse error-event data as JSON, require `ERR-TICKET-CATEGORY-REQUIRED`, preserve the category-guidance message, and verify no tool-call or done event
- [X] T002 [US1] Add ticket-creation tool exception assertions in `tests/contract/test_chat_stream.py` for `ERR-TICKET-CREATE-FAILED`, a non-empty message, and the existing intent-then-error/no-tool-call/no-done sequence
- [X] T003 [US2] Add password-reset tool exception assertions in `tests/contract/test_chat_stream.py` for `ERR-PASSWORD-RESET-FAILED`, a non-empty message, and the existing intent-then-error/no-tool-call/no-done sequence
- [X] T004 [P] [US1] Add silent ticket-creation exception coverage in `tests/contract/test_chat_stream.py` that requires the serialized message to contain the exception type name and a no-message indication
- [X] T005 [P] [US2] Add silent password-reset exception coverage in `tests/contract/test_chat_stream.py` that requires the serialized message to contain the exception type name and a no-message indication

**Checkpoint**: The focused contract suite distinguishes all three required envelopes and their existing terminal stream lifecycle.

---

## Phase 2: User Story 1 - Receive Safe Ticket Creation Errors (Priority: P1) MVP

**Goal**: Produce consistent, parseable, non-empty error envelopes for missing ticket categories and ticket-creation tool failures while preserving category inference and ticket success behavior.

**Independent Test**: Submit a category-less ticket request and simulate a ticket-create exception; each produces `action_request` followed by the specified error envelope, with no tool-call or done event.

### Implementation for User Story 1

- [X] T006 [US1] Update the missing-category branch in `create_ticket_node` within `src/agent/nodes.py` to serialize `ERR-TICKET-CATEGORY-REQUIRED` and the existing category-guidance message into `state["error"]`
- [X] T007 [US1] Update the ticket-creation tool exception handler in `create_ticket_node` within `src/agent/nodes.py` to serialize `ERR-TICKET-CREATE-FAILED` and a non-empty exception message, using the exception type-name fallback when needed
- [X] T008 [US1] Preserve existing category/priority inference, tool invocation, ticket success response, and intent-then-error/no-tool-call/no-done behavior in `src/agent/nodes.py` by modifying only the two specified error values
- [X] T009 [US1] Run the ticket-creation error and success contract coverage in `tests/contract/test_chat_stream.py` and correct only failures caused by `create_ticket_node` changes

**Checkpoint**: Ticket category guidance and ticket tool failures use the structured error contract without changing ticket creation success behavior.

---

## Phase 3: User Story 2 - Receive Safe Password Reset Errors (Priority: P1)

**Goal**: Produce a consistent, parseable, non-empty error envelope when a valid password-reset tool call fails while preserving success and escalation flows.

**Independent Test**: Simulate a password-reset tool exception after valid request validation; the stream emits `action_request` then an `ERR-PASSWORD-RESET-FAILED` error envelope, with no tool-call or done event.

### Implementation for User Story 2

- [X] T010 [US2] Update the password-reset tool exception handler in `check_password_reset_node` within `src/agent/nodes.py` to serialize `ERR-PASSWORD-RESET-FAILED` and a non-empty exception message, using the exception type-name fallback when needed
- [X] T011 [US2] Preserve existing employee-ID validation, escalation precedence, tool invocation, and success/escalation stream behavior in `src/agent/nodes.py` by modifying only the specified exception error value
- [X] T012 [US2] Run the password-reset exception, success, and escalation contract coverage in `tests/contract/test_chat_stream.py` and correct only failures caused by `check_password_reset_node` changes

**Checkpoint**: Password-reset tool failures use the structured error contract without changing successful or escalated reset behavior.

---

## Phase 4: Cross-Cutting Verification

**Purpose**: Confirm the repaired error envelopes coexist with all existing chat-stream behavior.

- [X] T013 Run the complete regression suite with `.venv/Scripts/python.exe -m pytest -q tests` from the repository root
- [X] T014 Run the manual stream-payload checks in `specs/016-ticket-password-error-envelopes/quickstart.md` and confirm all three error payloads parse to an error code and non-empty message

**Checkpoint**: Existing ticket, password-reset, and broader chat behaviors remain runnable with consistent terminal errors.

## Dependencies & Execution Order

- **Phase 1**: Complete T001-T005 before changing runtime behavior so the expected envelopes are defined by tests.
- **User Story 1**: Complete T006-T009 after Phase 1. T006 and T007 touch the same function and must be sequential.
- **User Story 2**: Complete T010-T012 after Phase 1. It is conceptually independent of User Story 1, but all runtime edits share `src/agent/nodes.py`; implement sequentially to avoid conflict.
- **Phase 4**: Complete after both user stories.

## Parallel Opportunities

```text
After contract scaffolding is in place:
- T004 and T005 can be authored in parallel because they cover separate failure paths.
- Ticket and password-reset behavior can be independently reviewed and validated, but their runtime edits are serialized because both modify src/agent/nodes.py.
```

## Implementation Strategy

### MVP First

1. Complete T001, T002, and T004 to capture ticket-category and ticket-tool failure contracts.
2. Complete T006-T009 to deliver structured ticket errors while retaining ticket success behavior.
3. Complete the password-reset path through T010-T012.
4. Run T013-T014 for final regression and stream-payload verification.

### Incremental Delivery

1. Deliver User Story 1 after focused ticket error and success tests pass.
2. Deliver User Story 2 after password-reset exception, success, and escalation tests pass.
3. Confirm the full suite and documented manual stream checks before release.

## Format Validation

Every task uses the required checklist format: checkbox, sequential task ID, applicable user-story label, and exact file path or validation target.