# Tasks: PII Redaction and Prompt Injection Guard

**Input**: Design documents from /specs/006-pii-injection-guard/

**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Contract tests are included because acceptance criteria explicitly require redaction, blocked-injection, and clean-message regression verification.

**Organization**: Tasks are grouped by user story so each story can be implemented and validated independently.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Create security module scaffolding and shared constants for the guardrail slice.

- [X] T001 Create security package initialization in src/security/__init__.py
- [X] T002 Create redaction module skeleton for redact_pii in src/security/redact.py
- [X] T003 Create injection detection module skeleton for detect_prompt_injection in src/security/injection.py
- [X] T004 Add blocked-injection error constants in src/agent/prompts.py

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Implement pre-classification safety primitives and wire them into graph flow.

**CRITICAL**: No user story work starts until this phase is complete.

- [X] T005 [P] Extend guardrail-related state fields in src/agent/state.py
- [X] T006 [P] Implement email placeholder substitution logic in src/security/redact.py
- [X] T007 [P] Implement phone placeholder substitution logic in src/security/redact.py
- [X] T008 [P] Implement whitespace normalization utility for safety matching in src/security/injection.py
- [X] T009 Implement case-insensitive override phrase and paraphrase-style pattern matching in src/security/injection.py
- [X] T010 Implement pre-classification guardrail node that runs detect_prompt_injection then redact_pii in src/agent/nodes.py
- [X] T011 Route graph entry through guardrail node before classify_intent in src/agent/graph.py
- [X] T012 Implement blocked-first stream emission path using JSON-encoded error data in src/api/routes/chat.py

**Checkpoint**: Guardrail checks execute before classification and can short-circuit blocked messages.

---

## Phase 3: User Story 1 - Protect Sensitive User Data Before Processing (Priority: P1) MVP

**Goal**: Redact email/phone PII in non-blocked messages while preserving normal downstream behavior.

**Independent Test**: Send a message containing email or phone data and verify normal completion with redacted placeholders used in downstream processing.

### Tests for User Story 1

- [X] T013 [P] [US1] Add contract test for email redaction with normal completion flow in tests/contract/test_chat_stream.py
- [X] T014 [P] [US1] Add contract test for phone redaction with normal completion flow in tests/contract/test_chat_stream.py

### Implementation for User Story 1

- [X] T015 [US1] Ensure guardrail node rewrites state message with redacted placeholders for non-blocked requests in src/agent/nodes.py
- [X] T016 [US1] Ensure redacted message is the one passed to downstream direct_response and policy_question processing in src/agent/nodes.py
- [X] T017 [US1] Preserve intent-first stream sequence for legitimate redacted requests in src/api/routes/chat.py

**Checkpoint**: PII redaction works and legitimate requests still complete through existing intent paths.

---

## Phase 4: User Story 2 - Block Prompt Injection Attempts Early (Priority: P1)

**Goal**: Detect and block injection attempts before classification, retrieval, tool calls, or LLM calls.

**Independent Test**: Send injection attempts including case/spacing variants and paraphrase-style attempts and verify only blocked error event is emitted.

### Tests for User Story 2

- [X] T018 [P] [US2] Add contract test for case/spacing variant injection attempt returning only blocked error in tests/contract/test_chat_stream.py
- [X] T019 [P] [US2] Add contract test for paraphrase-style injection attempt returning only blocked error in tests/contract/test_chat_stream.py
- [X] T020 [P] [US2] Add contract test asserting blocked response data JSON includes ERR-PROMPT-INJECTION-BLOCKED and Request blocked for safety. in tests/contract/test_chat_stream.py

### Implementation for User Story 2

- [X] T021 [US2] Implement blocked guardrail state outcome with fixed code/message payload values in src/agent/nodes.py
- [X] T022 [US2] Ensure blocked guardrail path bypasses classify_intent and response-generation nodes in src/agent/graph.py
- [X] T023 [US2] Ensure blocked stream emits error as first event with no intent/token/tool_call/done events in src/api/routes/chat.py

**Checkpoint**: Injection attempts are deterministically blocked before any downstream processing.

---

## Phase 5: User Story 3 - Preserve Existing Behavior for Clean Requests (Priority: P2)

**Goal**: Keep clean-message and prior stage behavior unchanged except for early guardrail insertion.

**Independent Test**: Clean messages and existing stage 1-4 scenarios continue passing unchanged.

### Tests for User Story 3

- [X] T024 [P] [US3] Add contract test proving clean message behavior is unaffected (intent and completion sequence unchanged) in tests/contract/test_chat_stream.py
- [X] T025 [P] [US3] Add regression assertion that existing validation/disconnect/non-policy flows remain unchanged in tests/contract/test_chat_stream.py

### Implementation for User Story 3

- [X] T026 [US3] Keep existing intent classification logic unchanged while inserting pre-classification guardrail call path in src/agent/graph.py
- [X] T027 [US3] Verify no runtime behavior changes are introduced in src/rag/** and src/tools/** for this slice via focused scope checks in tests/contract/test_chat_stream.py

**Checkpoint**: Existing behavior remains stable for clean traffic and legacy stage scenarios.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Finalize documentation and verification evidence for this slice.

- [X] T028 [P] Update blocked and redaction stream examples in specs/006-pii-injection-guard/contracts/http-api.md
- [X] T029 [P] Update scenario and expected outputs in specs/006-pii-injection-guard/quickstart.md
- [X] T030 Run full test suite and record verification notes in specs/006-pii-injection-guard/quickstart.md

---

## Dependencies & Execution Order

### Phase Dependencies

- Setup (Phase 1): no dependencies.
- Foundational (Phase 2): depends on Setup completion and blocks all user stories.
- User Story phases (Phase 3-5): depend on Foundational completion.
- Polish (Phase 6): depends on completed user stories.

### User Story Dependencies

- User Story 1 (P1): starts after Foundational completion.
- User Story 2 (P1): starts after Foundational completion and can run after US1 baseline is in place.
- User Story 3 (P2): starts after US1 and US2 integration to verify no regressions.

### Within Each User Story

- Write contract tests first and verify they fail before implementation.
- Complete node/graph guardrail behavior before route-level stream assertions.
- Complete each story checkpoint before moving to next story.

### Parallel Opportunities

- T005, T006, T007, and T008 can run in parallel.
- T013 and T014 can run in parallel.
- T018, T019, and T020 can run in parallel.
- T024 and T025 can run in parallel.
- T028 and T029 can run in parallel.

---

## Parallel Example: User Story 1

- Task T013 in tests/contract/test_chat_stream.py
- Task T014 in tests/contract/test_chat_stream.py

## Parallel Example: User Story 2

- Task T018 in tests/contract/test_chat_stream.py
- Task T019 in tests/contract/test_chat_stream.py
- Task T020 in tests/contract/test_chat_stream.py

---

## Implementation Strategy

### MVP First (User Story 1)

1. Complete Phase 1 Setup.
2. Complete Phase 2 Foundational tasks.
3. Complete Phase 3 User Story 1.
4. Validate User Story 1 independently before moving on.

### Incremental Delivery

1. Add injection block handling and blocked-event contract behavior in User Story 2.
2. Add clean-message regression protections in User Story 3.
3. Finish docs polish and full-suite verification in Phase 6.

### Scope Guardrails

- Do not add tasks for RAG feature expansion or retrieval logic changes.
- Do not add tasks for new tools, observability modules, or frontend work.
- Do not add tasks for LLM configuration rewrites or ticket-tool changes.
- Do not modify intent classification logic beyond inserting the earlier guardrail check in the pipeline.
