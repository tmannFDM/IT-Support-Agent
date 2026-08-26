# Tasks: Injection Pattern Expansion

**Input**: Design documents from /specs/007-injection-pattern-expansion/

**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Contract tests are included because acceptance criteria explicitly require one new missed-phrase regression case and unchanged existing behavior.

**Organization**: Tasks are grouped by user story so each story can be implemented and validated independently.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Confirm strictly scoped files and preserve existing behavior boundaries.

- [X] T001 Confirm implementation scope is limited to src/security/injection.py and tests/contract/test_chat_stream.py

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Prepare pattern-list data update with no logic modifications.

**CRITICAL**: No user story work starts until this phase is complete.

- [X] T002 Verify detect_prompt_injection matching logic remains unchanged in src/security/injection.py

**Checkpoint**: Change boundary is established as data-only pattern expansion.

---

## Phase 3: User Story 1 - Catch More Injection Variants Deterministically (Priority: P1) MVP

**Goal**: Expand INJECTION_PATTERNS with the provided dismissal, role-override, extraction, and explicit-override phrases.

**Independent Test**: Requests containing newly added phrases are blocked under existing behavior.

### Implementation for User Story 1

- [X] T003 [US1] Add instruction-dismissal phrase variants to INJECTION_PATTERNS in src/security/injection.py
- [X] T004 [US1] Add persona/role-override phrase variants to INJECTION_PATTERNS in src/security/injection.py
- [X] T005 [US1] Add system-prompt-extraction and explicit-override phrase variants to INJECTION_PATTERNS in src/security/injection.py

**Checkpoint**: Pattern list includes all newly requested phrase variants.

---

## Phase 4: User Story 2 - Preserve Existing Detection Mechanics and Response Shape (Priority: P1)

**Goal**: Keep detection mechanism, routing, and blocked response shape unchanged.

**Independent Test**: Existing blocked response behavior remains identical while new phrases are recognized.

### Implementation for User Story 2

- [X] T006 [US2] Ensure only INJECTION_PATTERNS data changes with no detection algorithm edits in src/security/injection.py
- [X] T007 [US2] Run existing blocked-behavior contract checks in tests/contract/test_chat_stream.py to confirm unchanged response shape

**Checkpoint**: Behavior is unchanged outside expanded phrase coverage.

---

## Phase 5: User Story 3 - Cover Previously Missed Phrase with Test (Priority: P2)

**Goal**: Add one regression test for the missed phrase forget everything you were told before this message.

**Independent Test**: New test passes and blocked-only behavior is asserted for the missed phrase.

### Tests for User Story 3

- [X] T008 [US3] Add contract test for forget everything you were told before this message blocked outcome in tests/contract/test_chat_stream.py

### Implementation for User Story 3

- [X] T009 [US3] Run contract tests to verify new phrase case and existing blocked behavior in tests/contract/test_chat_stream.py

**Checkpoint**: Missed phrase is now explicitly covered by regression testing.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final validation of unchanged overall system behavior.

- [X] T010 Run full test suite to confirm phrase expansion and single new regression case introduce no unrelated changes via tests/contract/test_chat_stream.py

---

## Dependencies & Execution Order

### Phase Dependencies

- Setup (Phase 1): no dependencies.
- Foundational (Phase 2): depends on Setup completion and blocks user stories.
- User Story phases (Phase 3-5): depend on Foundational completion.
- Polish (Phase 6): depends on completed user stories.

### User Story Dependencies

- User Story 1 (P1): starts after Foundational completion.
- User Story 2 (P1): starts after User Story 1 and validates unchanged behavior boundaries.
- User Story 3 (P2): starts after User Story 1 because it validates a newly added phrase.

### Within Each User Story

- Update phrase data first.
- Add missed-phrase test case.
- Execute regression verification.

### Parallel Opportunities

- T003, T004, and T005 can be prepared in parallel as phrase-group additions in the same target file but applied sequentially.
- T007 and T008 can run in parallel using separate terminals and files.

---

## Parallel Example: User Story 1

- Task T003 in src/security/injection.py
- Task T004 in src/security/injection.py
- Task T005 in src/security/injection.py

## Parallel Example: User Story 3

- Task T008 in tests/contract/test_chat_stream.py
- Task T009 in tests/contract/test_chat_stream.py

---

## Implementation Strategy

### MVP First (User Story 1)

1. Complete Phase 1 Setup.
2. Complete Phase 2 Foundational tasks.
3. Complete Phase 3 User Story 1.
4. Validate phrase expansion before moving on.

### Incremental Delivery

1. Apply phrase list additions.
2. Add one missed-phrase contract test.
3. Run contract then full regression suite.

### Scope Guardrails

- Do not add tasks for any file outside src/security/injection.py and tests/contract/test_chat_stream.py.
- Do not add tasks for logic/routing/event-shape changes.
- Do not add tasks for RAG/tools/observability/frontend/LLM configuration changes.
