# Tasks: Unify Local LLM Configuration

**Input**: Design documents from /specs/005-unify-local-llm-config/

**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: No new tests are added. Verification is limited to running existing tests and confirming unchanged pass behavior.

**Organization**: Tasks are grouped by user story so each story can be implemented and validated independently.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Prepare shared local configuration alignment scope for agent generation paths.

- [X] T001 [P] Define single shared local LLM endpoint and model constants in src/agent/prompts.py
- [X] T002 Remove legacy OpenAI default constants from active configuration exports in src/agent/prompts.py

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Align agent-node imports and shared configuration usage before story-level completion.

**CRITICAL**: No user story work starts until this phase is complete.

- [X] T003 [P] Update imports to use shared local LLM constants in src/agent/nodes.py
- [X] T004 Remove legacy OpenAI constant references and API-key dependency checks in src/agent/nodes.py

**Checkpoint**: Shared configuration plumbing is in place for both conversational paths.

---

## Phase 3: User Story 1 - Consistent Local Response Generation (Priority: P1) MVP

**Goal**: Ensure direct_response and policy_question generation both resolve endpoint/model from one shared local configuration.

**Independent Test**: Validate both response paths continue to stream expected intent and token/done sequences while using shared local configuration.

### Implementation for User Story 1

- [X] T005 [US1] Refactor direct_response generation call to use shared local Ollama endpoint in src/agent/nodes.py
- [X] T006 [US1] Refactor direct_response model selection to use the shared model constant in src/agent/nodes.py
- [X] T007 [US1] Keep policy_question generation on the same shared endpoint/model constants as direct_response in src/agent/nodes.py

**Checkpoint**: Both conversational generation paths use one shared local backend configuration.

---

## Phase 4: User Story 2 - Remove Unused External-Provider Defaults (Priority: P1)

**Goal**: Eliminate active OpenAI-specific configuration usage from this conversational subsystem.

**Independent Test**: Confirm no active code path requires external-provider API key or OpenAI default constants.

### Implementation for User Story 2

- [X] T008 [P] [US2] Remove OpenAI-specific constant definitions from src/agent/prompts.py
- [X] T009 [P] [US2] Remove stale direct_response provider branches tied to OpenAI settings in src/agent/nodes.py
- [X] T010 [US2] Ensure direct_response and policy_question consume a single shared local configuration source in src/agent/nodes.py and src/agent/prompts.py

**Checkpoint**: External-provider defaults are no longer part of active conversational behavior.

---

## Phase 5: User Story 3 - Preserve Existing Stream and Regression Contracts (Priority: P2)

**Goal**: Keep stream contract behavior unchanged while applying the configuration correction.

**Independent Test**: Re-run existing stage-1/2/3/4 tests and confirm unchanged pass behavior.

### Implementation for User Story 3

- [X] T011 [US3] Run existing test suite command against tests/contract/test_chat_stream.py from repository root and confirm pass status remains unchanged
- [X] T012 [P] [US3] Verify no schema, routing, RAG, or ticket-tool files are modified outside src/agent/prompts.py and src/agent/nodes.py

**Checkpoint**: Correction is complete with existing contract behavior preserved.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final verification and delivery readiness for this narrow correction pass.

- [X] T013 [P] Confirm quickstart validation command and result note in specs/005-unify-local-llm-config/quickstart.md

---

## Dependencies & Execution Order

### Phase Dependencies

- Setup (Phase 1): no dependencies.
- Foundational (Phase 2): depends on Setup completion and blocks all user stories.
- User Story phases (Phase 3-5): depend on Foundational completion.
- Polish (Phase 6): depends on completed user stories.

### User Story Dependencies

- User Story 1 (P1): starts after Foundational completion.
- User Story 2 (P1): starts after User Story 1 shared-configuration baseline.
- User Story 3 (P2): starts after User Story 1 and User Story 2 to validate no regressions.

### Within Each User Story

- Complete configuration refactor tasks before verification tasks.
- Keep all source edits constrained to src/agent/prompts.py and src/agent/nodes.py.
- Complete story checkpoint before moving to the next story.

### Parallel Opportunities

- T001 and T003 can run in parallel after initial alignment agreement.
- T008 and T009 can run in parallel because they target different files.
- T012 and T013 can run in parallel after implementation edits are complete.

---

## Parallel Example: User Story 1

- Task T001 in src/agent/prompts.py
- Task T003 in src/agent/nodes.py

## Parallel Example: User Story 2

- Task T008 in src/agent/prompts.py
- Task T009 in src/agent/nodes.py

---

## Implementation Strategy

### MVP First (User Story 1)

1. Complete Phase 1 Setup.
2. Complete Phase 2 Foundational tasks.
3. Complete Phase 3 User Story 1.
4. Validate User Story 1 behavior before moving on.

### Incremental Delivery

1. Add provider-default removal in User Story 2.
2. Run unchanged-test verification in User Story 3.
3. Finish quickstart verification note in Phase 6.

### Scope Guardrails

- Do not add tasks for RAG ingestion/retrieval changes.
- Do not add tasks for tools, security, or observability.
- Do not add tasks for new tests; only run existing tests.
- Do not add tasks for schema or routing changes.
