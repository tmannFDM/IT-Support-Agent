# Tasks: Error Envelope Fallback (Feature 015)

**Input**: Design documents from `/specs/015-error-envelope-fallback/`

**Prerequisites**: [plan.md](plan.md), [spec.md](spec.md), [research.md](research.md), [data-model.md](data-model.md), and [error-event-envelope.md](contracts/error-event-envelope.md)

**Scope**: Only `generate_response_node`, `answer_policy_question_node`, and `parseErrorPayload`; no schemas, nodes, event lifecycle, or other files are in scope except the existing contract test file needed to verify the backend repair.

**Tests**: Existing generation-failure contract tests must be updated and run. The frontend project has no dedicated frontend test harness in scope; parser behavior is validated by TypeScript/Vite build and the quickstart cases.

## Phase 1: Contract Test Preparation

**Purpose**: Define the corrected backend error-event assertions before modifying generation handlers.

- [X] T001 [US1] Update direct-response and policy-generation failure assertions in `tests/contract/test_chat_stream.py` to parse error-event data, require a non-empty message, verify the new path-specific error codes, and preserve intent-then-error with no done
- [X] T002 [US1] Add empty-message exception coverage in `tests/contract/test_chat_stream.py` that verifies the serialized error message contains the exception type name and a no-message indication for both generation paths

**Checkpoint**: The focused contract suite specifies the corrected envelope and terminal event sequence.

---

## Phase 2: User Story 1 - Show Generation Failures Safely (Priority: P1) MVP

**Goal**: Ensure direct and policy generation exceptions produce consistent, categorized, non-empty serialized error envelopes without changing stream lifecycle.

**Independent Test**: Run `tests/contract/test_chat_stream.py` with mocked direct-response and policy LLM failures; each path emits its intent followed by one error with the documented code and non-empty message, and never emits done.

### Implementation for User Story 1

- [X] T003 [US1] Update `generate_response_node` exception handling in `src/agent/nodes.py` to serialize `ERR-LLM-GENERATION-FAILED` and a guaranteed non-empty exception message into `state["error"]`
- [X] T004 [US1] Update `answer_policy_question_node` exception handling in `src/agent/nodes.py` to serialize `ERR-POLICY-GENERATION-FAILED` and a guaranteed non-empty exception message into `state["error"]`
- [X] T005 [US1] Preserve the existing intent-then-error/no-done behavior in `src/agent/nodes.py` by changing only the two error payload values, not graph routing or event generation
- [X] T006 [US1] Run the focused generation-failure contract tests in `tests/contract/test_chat_stream.py` and correct only failures caused by the two updated exception handlers

**Checkpoint**: Both generation paths deliver a valid error envelope and preserve their current terminal stream behavior.

---

## Phase 3: User Story 2 - Tolerate Invalid Error Events (Priority: P1)

**Goal**: Ensure the chat error parser returns a safe non-empty fallback instead of throwing for empty or malformed error event data.

**Independent Test**: Build the frontend and manually exercise the quickstart parser cases for empty, whitespace, invalid JSON, primitive JSON, missing-message objects, empty-message objects, and a valid non-empty envelope.

### Implementation for User Story 2

- [X] T007 [US2] Update `parseErrorPayload` in `frontend/src/api/chatStream.ts` so empty or whitespace-only data returns the existing non-empty fallback without attempting unsafe parsing
- [X] T008 [US2] Update `parseErrorPayload` in `frontend/src/api/chatStream.ts` so invalid JSON, primitives, missing messages, and empty messages return the existing non-empty fallback without throwing
- [X] T009 [US2] Preserve valid error-envelope behavior in `frontend/src/api/chatStream.ts` by returning the supplied non-empty message from a valid payload
- [X] T010 [US2] Run `npm.cmd run build` from `frontend/` and manually verify the parser cases from `specs/015-error-envelope-fallback/quickstart.md`

**Checkpoint**: The frontend safely renders every malformed error event with a user-safe fallback and retains valid error messages.

---

## Phase 4: Cross-Cutting Verification

**Purpose**: Confirm the repaired contract works across the existing chat stream without expanding scope.

- [X] T011 Run the complete backend regression suite with `.venv/Scripts/python.exe -m pytest -q tests` from the repository root
- [X] T012 Run the end-to-end generation-failure sequence in `specs/015-error-envelope-fallback/quickstart.md` and confirm the interface remains interactive after each terminal error event

**Checkpoint**: The existing vertical slice remains runnable with safe failure behavior.

## Dependencies & Execution Order

- **Phase 1**: Must complete before User Story 1 to establish the revised backend contract assertions.
- **User Story 1**: Depends on Phase 1; T003 and T004 modify the same file and must be completed sequentially. T005 and T006 follow both handler changes.
- **User Story 2**: Has no code dependency on User Story 1 and can proceed in parallel after Phase 1; its tasks are sequential because they modify the same parser.
- **Phase 4**: Depends on both user stories.

## Parallel Opportunities

```text
After T002 completes:
- Developer A: T003-T006 in src/agent/nodes.py and tests/contract/test_chat_stream.py
- Developer B: T007-T010 in frontend/src/api/chatStream.ts
```

## Implementation Strategy

### MVP First

1. Complete T001-T006 to deliver valid, non-empty backend generation-failure envelopes.
2. Run the focused backend contract tests and verify the existing `intent → error` termination behavior.
3. Complete T007-T010 to make frontend error handling resilient to invalid legacy or faulty payloads.
4. Finish T011-T012 to verify the complete vertical slice.

### Incremental Delivery

1. Deploy User Story 1 once both generation paths produce categorized, non-empty envelopes.
2. Deploy User Story 2 once the frontend tolerates malformed error data.
3. Verify the complete regression suite and the end-to-end failure sequence.

## Format Validation

Every task uses the required checklist format: checkbox, sequential ID, applicable user-story label, and exact file path or executable validation target.