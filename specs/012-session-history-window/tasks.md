# Tasks: In-Session Conversation History Window

**Input**: Design documents from `/specs/012-session-history-window/`

**Prerequisites**: `plan.md` (required), `spec.md` (required), `research.md`, `data-model.md`, `contracts/`

**Tests**: Contract tests are included because acceptance criteria explicitly require behavior verification for context usage, session isolation, bounded eviction, and tool-path independence.

**Organization**: Tasks are grouped by user story so each story can be implemented and tested independently.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Establish feature constants and test scaffolding for the session-history slice.

- [X] T001 Define session-history constants (window size = 5) in src/agent/session_history.py
- [X] T002 Add session-history reset fixture support in tests/contract/test_chat_stream.py

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Build shared session-history primitives required by all stories.

**⚠️ CRITICAL**: No user story implementation begins until these primitives are complete.

- [X] T003 Implement SessionExchange typed structure with redacted-only fields in src/agent/session_history.py
- [X] T004 Implement per-session in-memory store container keyed by session_id in src/agent/session_history.py
- [X] T005 Implement append-with-oldest-eviction sliding window logic in src/agent/session_history.py
- [X] T006 Implement history-to-LLM-messages projection helper preserving turn order in src/agent/session_history.py
- [X] T007 [P] Add helper tests for store reset/get/append behavior in tests/contract/test_chat_stream.py

**Checkpoint**: Shared history store and projection helpers are ready for story-specific wiring.

---

## Phase 3: User Story 1 - Contextual Follow-Up Answers (Priority: P1) 🎯 MVP

**Goal**: Same-session follow-up questions in direct and policy paths use recent turns as prior LLM context.

**Independent Test**: Send two related requests in the same session and verify the second LLM call payload includes prior turn messages from the first request.

### Tests for User Story 1

- [X] T008 [P] [US1] Add contract test capturing direct-response LLM messages list includes same-session prior turn in tests/contract/test_chat_stream.py
- [X] T009 [P] [US1] Add contract test capturing policy-response LLM messages list includes same-session prior turn in tests/contract/test_chat_stream.py

### Implementation for User Story 1

- [X] T010 [US1] Extend call_llm_direct_response signature to accept optional prior history messages in src/agent/nodes.py
- [X] T011 [US1] Extend call_llm_policy_response signature to accept optional prior history messages in src/agent/nodes.py
- [X] T012 [US1] Inject session history into direct_response prompt assembly path only in src/agent/nodes.py
- [X] T013 [US1] Inject session history into policy_question prompt assembly path only in src/agent/nodes.py
- [X] T014 [US1] Append completed redacted user+assistant exchange to session history only after done event in src/api/routes/chat.py

**Checkpoint**: US1 follow-up continuity is functional for direct and policy LLM calls.

---

## Phase 4: User Story 2 - Session-Isolated Short-Term Memory (Priority: P1)

**Goal**: Session history is strictly isolated by session_id, including when user_id is the same.

**Independent Test**: Seed history in session A, then verify first request in new session B has no inherited prior turns in LLM payload.

### Tests for User Story 2

- [X] T015 [P] [US2] Add contract test proving new session_id has empty history despite same user_id in tests/contract/test_chat_stream.py
- [X] T016 [P] [US2] Add contract test proving no cross-session leakage when two sessions interleave requests in tests/contract/test_chat_stream.py

### Implementation for User Story 2

- [X] T017 [US2] Ensure session-history retrieval helpers default unknown session_id to empty window in src/agent/session_history.py
- [X] T018 [US2] Wire per-request session_id lookup for prior-turn retrieval in src/agent/nodes.py

**Checkpoint**: US2 guarantees session isolation and empty-start behavior for new sessions.

---

## Phase 5: User Story 3 - Bounded History and Stable Existing Behavior (Priority: P2)

**Goal**: History remains bounded at 5 exchanges and does not alter tool-invoking path behavior.

**Independent Test**: Complete six exchanges in one session to verify oldest-turn eviction; confirm tool path tests still pass with seeded history.

### Tests for User Story 3

- [X] T019 [P] [US3] Add contract test verifying sixth completed exchange evicts oldest and retains newest five in tests/contract/test_chat_stream.py
- [X] T020 [P] [US3] Add contract test proving ticket-status/password-reset/ticket-creation behavior is unchanged with pre-seeded history in tests/contract/test_chat_stream.py

### Implementation for User Story 3

- [X] T021 [US3] Confirm append path stores redacted state message and final response text only in src/api/routes/chat.py
- [X] T022 [US3] Keep action-request extraction/routing helpers unchanged and history-independent in src/agent/nodes.py

**Checkpoint**: US3 enforces bounded memory and preserves stage 1-8 tool-path behavior.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final verification and docs alignment for the slice.

- [X] T023 [P] Add concise session-history behavior notes to specs/012-session-history-window/quickstart.md
- [X] T024 Run contract suite for chat stream updates with ./.venv/Scripts/python.exe -m pytest -q tests/contract/test_chat_stream.py
- [X] T025 Run full regression suite with ./.venv/Scripts/python.exe -m pytest -q tests

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies; start immediately.
- **Phase 2 (Foundational)**: Depends on Phase 1; blocks all user-story work.
- **Phase 3 (US1)**: Depends on Phase 2.
- **Phase 4 (US2)**: Depends on Phase 2 and uses US1 wiring for prompt-context verification.
- **Phase 5 (US3)**: Depends on Phase 2 and validates bounded behavior plus regression safety across US1/US2-enabled flow.
- **Phase 6 (Polish)**: Depends on all story phases.

### User Story Dependencies

- **US1 (P1)**: First MVP slice after foundational work.
- **US2 (P1)**: Depends on shared store primitives; can proceed after US1 prompt wiring exists.
- **US3 (P2)**: Depends on completed append and retrieval behavior from US1/US2.

### Within Each User Story

- Tests are written before implementation and should fail before code changes.
- Prompt/history helper wiring before append/finalization behavior assertions.
- Story-level checkpoint must pass before moving to next story.

---

## Parallel Opportunities

- `T007` can run in parallel with foundational implementation once interfaces are stable.
- `T008` and `T009` can run in parallel (different test cases in same file with low merge risk if sequenced carefully).
- `T015` and `T016` can run in parallel.
- `T019` and `T020` can run in parallel.
- `T023` can run in parallel with final verification runs.

## Parallel Example: User Story 1

```bash
# Parallel test authoring tasks:
T008 Add direct-response history-injection contract test in tests/contract/test_chat_stream.py
T009 Add policy-response history-injection contract test in tests/contract/test_chat_stream.py

# Parallel implementation opportunities (after tests are in place):
T010 Extend direct LLM call signature in src/agent/nodes.py
T011 Extend policy LLM call signature in src/agent/nodes.py
```

## Parallel Example: User Story 2

```bash
# Parallel test tasks:
T015 Add new-session isolation contract test in tests/contract/test_chat_stream.py
T016 Add interleaved-session leakage contract test in tests/contract/test_chat_stream.py
```

## Parallel Example: User Story 3

```bash
# Parallel test tasks:
T019 Add bounded-window eviction contract test in tests/contract/test_chat_stream.py
T020 Add tool-path independence contract test in tests/contract/test_chat_stream.py
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1 and Phase 2.
2. Complete Phase 3 (US1).
3. Validate same-session follow-up continuity for direct/policy paths.
4. Pause for MVP demo/verification.

### Incremental Delivery

1. Add US1 for follow-up continuity.
2. Add US2 for strict session isolation guarantees.
3. Add US3 for bounded-window guarantees and unchanged tool behavior.
4. Finish with quickstart notes and full regression verification.

### Safety Strategy

1. Keep all tool-invoking extraction/routing helpers unchanged.
2. Keep long-term memory module untouched.
3. Verify no behavior drift with targeted contract tests and full suite run.

---

## Notes

- All tasks include exact file paths and are constrained to current session-history slice scope.
- Out-of-scope items are intentionally excluded: long-term memory changes, ticket/password tool changes, RAG internals, guardrail logic changes, Arize Phoenix, Promptfoo, and React frontend.
- Checklist format is enforced for every task entry.
