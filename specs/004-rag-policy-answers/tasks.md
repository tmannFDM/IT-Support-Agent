# Tasks: RAG Policy Answers Slice

**Input**: Design documents from /specs/004-rag-policy-answers/

**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Contract tests are included because acceptance criteria explicitly require grounded-answer, fallback, cross-category, and regression verification.

**Organization**: Tasks are grouped by user story so each story can be implemented and validated independently.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Add RAG slice dependencies and file scaffolding.

- [X] T001 Add ChromaDB and sentence-transformers dependencies in requirements.txt
- [X] T002 Create RAG package initialization in src/rag/__init__.py
- [X] T003 Create RAG module skeleton files in src/rag/embeddings.py, src/rag/ingest.py, and src/rag/retrieve.py

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Build shared policy corpus ingestion and retrieval infrastructure required by all stories.

**CRITICAL**: No user story work starts until this phase is complete.

- [X] T004 [P] Implement local all-MiniLM-L6-v2 embedding loader in src/rag/embeddings.py
- [X] T005 [P] Implement markdown header parsing for Policy Category metadata in src/rag/ingest.py
- [X] T006 Implement conservative section/paragraph chunking for policy docs in src/rag/ingest.py
- [X] T007 Implement ChromaDB collection setup and upsert flow for policy chunks in src/rag/ingest.py
- [X] T008 Implement retrieval top-k=3 query with score capture in src/rag/retrieve.py
- [X] T009 Implement relevance threshold filter at score >= 0.35 in src/rag/retrieve.py

**Checkpoint**: Policy corpus ingestion and thresholded retrieval are ready for agent integration.

---

## Phase 3: User Story 1 - Answer Policy Questions from Knowledge Base (Priority: P1) MVP

**Goal**: Return grounded policy answers with source-document citations for on-topic and cross-category policy questions.

**Independent Test**: Ask on-topic and cross-category policy questions and verify intent-first streaming, grounded token answer, citations, and done event.

### Tests for User Story 1

- [X] T010 [P] [US1] Add contract test for grounded on-topic policy answer sequence in tests/contract/test_chat_stream.py
- [X] T011 [P] [US1] Add contract test for cross-category retrieval using multiple source_document values in tests/contract/test_chat_stream.py

### Implementation for User Story 1

- [X] T012 [US1] Implement answer_policy_question node retrieval + context assembly in src/agent/nodes.py
- [X] T013 [US1] Implement grounded-answer Ollama llama3.2:3b call path in src/agent/nodes.py
- [X] T014 [US1] Append source_document filename citations to final policy answer text in src/agent/nodes.py
- [X] T015 [US1] Route policy_question intent through answer_policy_question node in src/agent/graph.py
- [X] T016 [US1] Preserve intent then token then done stream flow for successful policy answers in src/api/routes/chat.py

**Checkpoint**: Grounded policy answering with citations is independently functional.

---

## Phase 4: User Story 2 - Fail Safe on Missing Relevant Policy Context (Priority: P1)

**Goal**: Return deterministic no-information fallback when retrieval context is insufficient, and preserve error semantics for generation failures.

**Independent Test**: Ask off-topic policy question and verify exact fallback text; simulate policy generation failure and verify intent -> error with no done.

### Tests for User Story 2

- [X] T017 [P] [US2] Add contract test for exact fallback response when no chunk meets 0.35 threshold in tests/contract/test_chat_stream.py
- [X] T018 [P] [US2] Add contract test for policy generation failure sequence intent then error without done in tests/contract/test_chat_stream.py

### Implementation for User Story 2

- [X] T019 [US2] Implement no-context branch returning exact fallback text in src/agent/nodes.py
- [X] T020 [US2] Ensure no-context branch skips LLM call in src/agent/nodes.py
- [X] T021 [US2] Preserve policy-generation failure as error state for route-level error event handling in src/agent/nodes.py

**Checkpoint**: No-context and generation-failure behavior is deterministic and independently testable.

---

## Phase 5: User Story 3 - Preserve Existing Non-Policy Behavior (Priority: P2)

**Goal**: Keep stage-1/stage-2/stage-3 behavior unchanged outside policy_question routing.

**Independent Test**: Re-run existing validation, disconnect, direct_response, and ticket_status contract checks with policy path integrated.

### Tests for User Story 3

- [X] T022 [P] [US3] Add regression assertion that stage-1 validation error contract remains unchanged in tests/contract/test_chat_stream.py
- [X] T023 [P] [US3] Add regression assertion that disconnect handling remains immediate stop with no post-disconnect events in tests/contract/test_chat_stream.py
- [X] T024 [P] [US3] Add regression assertion that ticket_status and direct_response flows remain unchanged in tests/contract/test_chat_stream.py

### Implementation for User Story 3

- [X] T025 [US3] Restrict policy routing changes to policy_question path only in src/agent/nodes.py
- [X] T026 [US3] Preserve existing non-policy event behavior while integrating policy path in src/api/routes/chat.py

**Checkpoint**: Non-policy behavior remains intact with policy RAG path enabled.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Finalize docs and verification evidence for this specific scope.

- [X] T027 [P] Update policy RAG contract examples and stream sequences in specs/004-rag-policy-answers/contracts/http-api.md
- [X] T028 [P] Update quickstart scenarios for grounded, fallback, and cross-category checks in specs/004-rag-policy-answers/quickstart.md
- [X] T029 Run full test suite and record verification notes in specs/004-rag-policy-answers/quickstart.md

---

## Dependencies & Execution Order

### Phase Dependencies

- Setup (Phase 1): no dependencies.
- Foundational (Phase 2): depends on Setup completion and blocks all user stories.
- User Story phases (Phase 3-5): depend on Foundational completion.
- Polish (Phase 6): depends on completed user stories.

### User Story Dependencies

- User Story 1 (P1): starts after Foundational completion.
- User Story 2 (P1): starts after User Story 1 retrieval/generation baseline exists.
- User Story 3 (P2): starts after User Story 1 and User Story 2 integration to validate regressions.

### Within Each User Story

- Write contract tests first and verify they fail before implementation.
- Implement retrieval/node logic before route-stream adjustments.
- Complete each story checkpoint before moving to next story.

### Parallel Opportunities

- T004 and T005 can run in parallel.
- T010 and T011 can run in parallel.
- T017 and T018 can run in parallel.
- T022, T023, and T024 can run in parallel.
- T027 and T028 can run in parallel.

---

## Parallel Example: User Story 1

- Task T010 in tests/contract/test_chat_stream.py
- Task T011 in tests/contract/test_chat_stream.py

## Parallel Example: User Story 3

- Task T022 in tests/contract/test_chat_stream.py
- Task T023 in tests/contract/test_chat_stream.py
- Task T024 in tests/contract/test_chat_stream.py

---

## Implementation Strategy

### MVP First (User Story 1)

1. Complete Phase 1 Setup.
2. Complete Phase 2 Foundational tasks.
3. Complete Phase 3 User Story 1.
4. Validate User Story 1 independently before moving on.

### Incremental Delivery

1. Add no-context fail-safe and generation-failure handling in User Story 2.
2. Add regression-preservation checks in User Story 3.
3. Finish documentation and full-suite verification in Phase 6.

### Scope Guardrails

- Do not add tasks for tools beyond policy Q&A RAG, PII redaction, prompt injection detection, long-term memory, Arize Phoenix, Promptfoo, or React frontend.
- Do not add tasks that modify ticket_status_lookup implementation or routing.
- Do not add tasks that alter stage-1/stage-2 validation, error-code, or disconnect semantics beyond policy_question routing integration.
