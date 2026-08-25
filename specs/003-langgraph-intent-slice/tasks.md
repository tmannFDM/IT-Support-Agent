# Tasks: LangGraph Intent Slice

**Input**: Design documents from `/specs/003-langgraph-intent-slice/`

**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Contract tests are included because acceptance criteria explicitly require stream sequence and regression verification.

**Organization**: Tasks are grouped by user story so each story can be implemented and validated independently.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Add LangGraph and LLM scaffolding prerequisites for this slice

- [X] T001 Add LangGraph and required LLM adapter dependencies in requirements.txt
- [X] T002 Create agent package initialization in src/agent/__init__.py
- [X] T003 Define environment configuration placeholders for LLM access in src/agent/prompts.py

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Shared graph and schema contract changes required before user story work

**CRITICAL**: No user story work starts until this phase is complete

- [X] T004 [P] Define AgentState and intent label types in src/agent/state.py
- [X] T005 [P] Extend ChatStreamEvent event_type to include intent in src/schemas/chat.py
- [X] T006 Implement classify_intent and generate_response node interfaces in src/agent/nodes.py
- [X] T007 Implement LangGraph graph assembly and entrypoint in src/agent/graph.py
- [X] T008 Add prompt templates for intent classification and direct response generation in src/agent/prompts.py

**Checkpoint**: Foundation ready for intent-routing story work

---

## Phase 3: User Story 1 - Classify and Route Chat Intent (Priority: P1) MVP

**Goal**: Route all messages through LangGraph and expose deterministic intent event first in stream

**Independent Test**: Send category-representative messages and confirm stream starts with intent event and non-direct intents return fixed placeholder sequence

### Tests for User Story 1

- [X] T009 [US1] Add contract tests for intent-first stream event across all intent categories in tests/contract/test_chat_stream.py
- [X] T010 [US1] Add contract tests for non-direct intents returning exact placeholder text and done termination in tests/contract/test_chat_stream.py

### Implementation for User Story 1

- [X] T011 [US1] Implement classify_intent node logic for five intent labels in src/agent/nodes.py
- [X] T012 [US1] Implement non-direct placeholder routing path with exact text in src/agent/nodes.py
- [X] T013 [US1] Wire /chat/stream to execute LangGraph flow and emit intent event before token events in src/api/routes/chat.py

**Checkpoint**: Intent routing and placeholder behavior are independently functional

---

## Phase 4: User Story 2 - Generate Real Direct Responses Through LangGraph (Priority: P1)

**Goal**: Produce real LLM direct responses and enforce direct-response failure sequence

**Independent Test**: direct_response requests stream intent -> token(s) -> done; LLM failure streams intent -> error and stops without done

### Tests for User Story 2

- [X] T014 [US2] Add contract test for direct_response success sequence intent then token events then done in tests/contract/test_chat_stream.py
- [X] T015 [US2] Add contract test for direct_response generation failure sequence intent then error without done in tests/contract/test_chat_stream.py

### Implementation for User Story 2

- [X] T016 [US2] Implement direct_response LLM call path in generate_response node in src/agent/nodes.py
- [X] T017 [US2] Emit stream sequence rules for direct_response success and failure in src/api/routes/chat.py
- [X] T018 [US2] Ensure no placeholder fallback is used on direct_response LLM failure in src/agent/nodes.py

**Checkpoint**: Direct-response generation and failure handling are independently functional

---

## Phase 5: User Story 3 - Preserve Stage-1 Reliability Contracts (Priority: P2)

**Goal**: Keep stage-1 validation, error shape, and disconnect behavior unchanged while introducing graph routing

**Independent Test**: Run existing stage-1 tests unchanged and verify no contract regressions

### Tests for User Story 3

- [X] T019 [US3] Extend contract tests to assert stage-1 validation and error-shape behavior remains unchanged in tests/contract/test_chat_stream.py
- [X] T020 [US3] Extend contract tests to assert disconnect behavior remains immediate stop with no post-disconnect events in tests/contract/test_chat_stream.py

### Implementation for User Story 3

- [X] T021 [US3] Integrate LangGraph routing in src/api/routes/chat.py without changing existing validation and exception handling interfaces
- [X] T022 [US3] Preserve existing disconnect checks while routing stream generation through graph execution in src/api/routes/chat.py

**Checkpoint**: Stage-1 reliability contracts remain intact with LangGraph flow enabled

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Finalize documentation and verification for this scoped slice

- [X] T023 [P] Update quickstart scenarios to reflect intent event sequencing and failure-path expectations in specs/003-langgraph-intent-slice/quickstart.md
- [X] T024 [P] Update API contract examples for intent event extension and stream sequences in specs/003-langgraph-intent-slice/contracts/http-api.md
- [X] T025 Run full test suite and record verification notes for this slice in specs/003-langgraph-intent-slice/quickstart.md

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies, starts immediately
- **Foundational (Phase 2)**: Depends on Setup and blocks all stories
- **User Stories (Phase 3-5)**: Depend on Foundational completion
- **Polish (Phase 6)**: Depends on completion of selected user stories

### User Story Dependencies

- **User Story 1 (P1)**: Starts after Foundational, no dependency on other stories
- **User Story 2 (P1)**: Starts after User Story 1 routing baseline is available
- **User Story 3 (P2)**: Starts after User Story 1/2 integration to validate regressions

### Within Each User Story

- Write contract tests first and verify they fail before implementation
- Implement node logic before chat route integration
- Complete stream sequence assertions before moving to next story

### Parallel Opportunities

- T004 and T005 can execute in parallel
- T009 and T010 can execute in parallel
- T014 and T015 can execute in parallel
- T023 and T024 can execute in parallel

---

## Parallel Example: User Story 1

```bash
Task: T009 Add contract tests for intent-first stream event
Task: T010 Add contract tests for non-direct placeholder path
```

## Parallel Example: User Story 2

```bash
Task: T014 Add direct_response success-sequence contract test
Task: T015 Add direct_response failure-sequence contract test
```

---

## Implementation Strategy

### MVP First (User Story 1)

1. Complete Setup and Foundational phases
2. Deliver User Story 1 intent routing and placeholder behavior
3. Validate intent-first sequence and placeholder contract

### Incremental Delivery

1. Add direct_response LLM generation (User Story 2)
2. Verify generation failure contract behavior
3. Run stage-1 regression verification (User Story 3)
4. Finalize quickstart and contract documentation updates

### Scope Guardrails

- Do not add tasks for RAG/ChromaDB, FastMCP tools, PII redaction, prompt injection detection, long-term memory, Phoenix, Promptfoo, or React frontend
- Do not add tasks that change stage-1 validation semantics, error-code catalog, or disconnect behavior beyond graph routing integration
