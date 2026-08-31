# Tasks: Long-Term User Memory Whitelist

**Input**: Design documents from `/specs/011-user-memory-whitelist/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/http-api.md

**Tests**: Contract tests are required for this slice by specification.

**Organization**: Tasks are grouped by user story for independent implementation and validation.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Add minimal memory module scaffolding and schema entry points.

- [X] T001 Create memory module scaffold and storage file path constants in src/memory/store.py
- [X] T002 [P] Create user memory schema module scaffold in src/schemas/user_memory.py
- [X] T003 [P] Export new user memory schema in src/schemas/__init__.py

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Build persistence and state primitives required by all user stories.

**⚠️ CRITICAL**: No user story work should begin until this phase is complete.

- [X] T004 Implement JSON file bootstrap/read helpers for user-memory records in src/memory/store.py
- [X] T005 Implement per-user upsert and retrieval helpers keyed by user_id in src/memory/store.py
- [X] T006 Add closed-whitelist UserMemoryFacts literals and validation in src/schemas/user_memory.py
- [X] T007 Add optional user memory facts fields to agent state in src/agent/state.py

**Checkpoint**: Foundational memory persistence and schema contracts are ready.

---

## Phase 3: User Story 1 - Capture and Persist Whitelisted User Facts (Priority: P1) 🎯 MVP

**Goal**: Persist valid whitelist facts from user messages with per-field independent extraction and validation.

**Independent Test**: Send explicit fact statements and verify valid fields are persisted, invalid candidates are ignored, and normal responses continue.

### Tests for User Story 1

- [X] T008 [P] [US1] Add contract test for storing a stated whitelist fact in tests/contract/test_chat_stream.py
- [X] T009 [P] [US1] Add contract test that mixed valid and non-whitelisted candidates stores only valid field in tests/contract/test_chat_stream.py

### Implementation for User Story 1

- [X] T010 [US1] Implement preferred_device_type keyword/pattern extraction in src/agent/nodes.py
- [X] T011 [US1] Implement office_region keyword/pattern extraction constrained to APAC/EMEA/AMER in src/agent/nodes.py
- [X] T012 [US1] Implement timezone abbreviation extraction constrained to whitelist in src/agent/nodes.py
- [X] T013 [US1] Implement per-field validation and partial-valid upsert orchestration in src/agent/nodes.py
- [X] T014 [US1] Wire extraction after redaction in guardrail flow and persist valid facts by user_id in src/agent/nodes.py

**Checkpoint**: User Story 1 captures and persists whitelist facts safely and independently.

---

## Phase 4: User Story 2 - Reuse Stored Facts Across Separate Sessions (Priority: P1)

**Goal**: Make persisted facts available for same user_id across different session_id values.

**Independent Test**: Persist fact in one session, use different session_id with same user_id, and verify facts are available in downstream processing.

### Tests for User Story 2

- [X] T015 [P] [US2] Add contract test for same user_id and different session_id retrieval in tests/contract/test_chat_stream.py
- [X] T016 [P] [US2] Add contract test for simulated restart durability via store reload in tests/contract/test_chat_stream.py

### Implementation for User Story 2

- [X] T017 [US2] Implement user_id-based fact readback into state before intent classification in src/agent/nodes.py
- [X] T018 [US2] Ensure memory store reload behavior preserves persisted records across simulated restart in src/memory/store.py

**Checkpoint**: User Story 2 validates cross-session and restart-safe memory retrieval.

---

## Phase 5: User Story 3 - Enforce Strict Whitelist and Non-Blocking Behavior (Priority: P1)

**Goal**: Keep memory optional for response flow while enforcing strict no-extra-field persistence.

**Independent Test**: Verify no-memory-content requests behave equivalently regardless of stored facts and no unsupported fields are persisted.

### Tests for User Story 3

- [X] T019 [P] [US3] Add contract test that no-memory-content request behaves identically with/without stored facts in tests/contract/test_chat_stream.py
- [X] T020 [P] [US3] Add contract test asserting non-whitelisted or redacted candidates are not persisted in tests/contract/test_chat_stream.py

### Implementation for User Story 3

- [X] T021 [US3] Pass optional stored facts into answer_policy_question_node context path without hard dependency in src/agent/nodes.py
- [X] T022 [US3] Pass optional stored facts into generate_response_node context path without hard dependency in src/agent/nodes.py
- [X] T023 [US3] Ensure no extra fields (message history, summaries, inferred preferences) are written by persistence helpers in src/memory/store.py

**Checkpoint**: User Story 3 enforces strict whitelist and preserves non-blocking response behavior.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Verify full slice correctness and no regressions outside scoped memory wiring.

- [X] T024 [P] Run chat-stream contract regression including new memory scenarios in tests/contract/test_chat_stream.py
- [X] T025 [P] Run full regression suite to confirm stage 1-7 behavior remains unchanged in tests/
- [X] T026 Update quickstart validation notes with executed commands and outcomes in specs/011-user-memory-whitelist/quickstart.md

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies.
- **Phase 2 (Foundational)**: Depends on Phase 1 and blocks all stories.
- **Phase 3 (US1)**: Depends on Phase 2.
- **Phase 4 (US2)**: Depends on Phase 2 and US1 persistence path.
- **Phase 5 (US3)**: Depends on Phase 2; validates optional context wiring and strict persistence boundaries.
- **Phase 6 (Polish)**: Depends on completion of all target stories.

### User Story Dependencies

- **US1 (P1)**: First MVP story, no dependency on other stories after foundational phase.
- **US2 (P1)**: Depends on US1 write path for cross-session retrieval verification.
- **US3 (P1)**: Depends on foundational persistence and optional context wiring; can proceed after core write/read primitives are in place.

### Within Each User Story

- Tests should be authored first and fail before implementation.
- Extraction helpers before guardrail wiring.
- Persistence helpers before cross-session/restart tests.
- Optional context wiring must not introduce required-memory preconditions.

### Parallel Opportunities

- Setup tasks T002 and T003 can run in parallel.
- US1 tests T008 and T009 can run in parallel.
- US2 tests T015 and T016 can run in parallel.
- US3 tests T019 and T020 can run in parallel.
- Final regression tasks T024 and T025 can run in parallel.

---

## Parallel Example: User Story 1

```bash
# Contract tests in parallel:
Task: "T008 Add contract test for storing a stated whitelist fact in tests/contract/test_chat_stream.py"
Task: "T009 Add contract test that mixed valid and non-whitelisted candidates stores only valid field in tests/contract/test_chat_stream.py"

# Extraction helpers can be developed in parallel once shared parsing utilities exist:
Task: "T010 Implement preferred_device_type keyword/pattern extraction in src/agent/nodes.py"
Task: "T011 Implement office_region keyword/pattern extraction constrained to APAC/EMEA/AMER in src/agent/nodes.py"
Task: "T012 Implement timezone abbreviation extraction constrained to whitelist in src/agent/nodes.py"
```

---

## Parallel Example: User Story 2

```bash
# Cross-session and restart durability tests in parallel:
Task: "T015 Add contract test for same user_id and different session_id retrieval in tests/contract/test_chat_stream.py"
Task: "T016 Add contract test for simulated restart durability via store reload in tests/contract/test_chat_stream.py"
```

---

## Implementation Strategy

### MVP First (US1)

1. Complete Phase 1 and Phase 2.
2. Complete Phase 3 (US1).
3. Validate whitelist capture and partial-valid persistence behavior.

### Incremental Delivery

1. Deliver US1 fact capture and safe persistence.
2. Add US2 cross-session retrieval and restart durability.
3. Add US3 optional-node context and strict non-blocking guarantees.
4. Run full regressions to confirm stage 1-7 behavior remains unchanged.

### Scope Guardrails

- Exclude Arize Phoenix, Promptfoo, and React frontend work.
- Do not modify ticket/password-reset/RAG/guardrail semantics beyond minimal memory read/write wiring.
