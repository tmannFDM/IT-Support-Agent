# Feature Specification: RAG Policy Answers Slice

**Feature Branch**: `[004-rag-policy-answers]`

**Created**: 2026-08-25

**Status**: Draft

**Input**: User description: "Extend the IT Support Ticketing System with the fourth vertical slice: RAG-based policy question answering, replacing the placeholder response for policy_question intent."

## Clarifications

### Session 2026-08-25

- Q: What minimum relevance score should be required before retrieved policy chunks are considered usable context for answering? (FR-009) -> A: 0.35 minimum score.
- Q: How should the policy answer expose provenance from retrieved chunks to show where the answer came from? (FR-008) -> A: Append source_document filename(s) in the final token answer.
- Q: What exact fixed fallback message should be returned when no policy chunks meet the 0.35 relevance threshold? (FR-009) -> A: I don't have information on that policy.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Answer Policy Questions from Knowledge Base (Priority: P1)

As an IT support user, I want policy questions to return grounded answers from the approved policy documents so I can trust the guidance.

**Why this priority**: Replacing placeholder policy responses with grounded answers is the core value of this slice.

**Independent Test**: Ask a question clearly covered by one existing policy document and verify the stream returns intent first, then a grounded answer whose facts are present in that document, then done.

**Acceptance Scenarios**:

1. **Given** a policy question whose answer is present in a single policy document, **When** the request is processed, **Then** the system retrieves relevant chunks, generates a context-grounded answer, streams `intent` then `token` content then `done`, and the answer content matches facts present in the source.
2. **Given** policy documents are ingested, **When** chunks are stored for retrieval, **Then** each chunk includes `policy_category` metadata from the file header field and `source_document` metadata from the filename.

---

### User Story 2 - Fail Safe on Missing Relevant Policy Context (Priority: P1)

As an IT support user, I want the system to explicitly tell me when policy information is unavailable so it does not hallucinate unsupported answers.

**Why this priority**: Safe refusal on low-relevance retrieval is required to prevent fabricated policy guidance.

**Independent Test**: Ask a policy question not covered by the policy corpus and verify the system skips generation, returns a fixed no-information response, and does not provide hallucinated policy details.

**Acceptance Scenarios**:

1. **Given** a policy question with no retrieved chunks above relevance threshold, **When** processing occurs, **Then** the system skips generation and returns a fixed "I don't have information on that policy" style response via token events.
2. **Given** generation service fails after successful retrieval, **When** processing occurs, **Then** the stream follows `intent` then `error` and terminates with no `done`.

---

### User Story 3 - Preserve Existing Non-Policy Behavior (Priority: P2)

As a product owner, I want stage-1/stage-2/stage-3 behaviors unchanged outside policy-question routing so prior slices remain stable.

**Why this priority**: The slice must add focused RAG capability without regressions in existing intent paths and contracts.

**Independent Test**: Re-run existing validation, disconnect, direct-response, and ticket-status contract flows to verify unchanged behavior.

**Acceptance Scenarios**:

1. **Given** non-policy intents (action_request, direct_response, escalation, blocked), **When** processed, **Then** their existing routing and stream behavior remain unchanged.
2. **Given** a policy question spanning two categories (for example VPN and password), **When** relevant chunks exist across categories, **Then** retrieval returns cross-category context and the answer remains grounded in retrieved content.

---

### Edge Cases

- What happens when policy documents include short sections with sparse wording? Chunking preserves section or paragraph coherence so retrievable content is complete enough to answer.
- How does the system handle policy questions that partially match multiple categories? Retrieval may return top chunks from multiple categories and answer synthesis must remain grounded only in returned context.
- What happens if a policy file is present but contains no extractable section text? Ingestion skips empty chunks and continues with remaining documents.
- How does the system handle retrieval scores below threshold for all candidates? It must return the fixed no-information response and skip generation.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST ingest the five existing markdown policy files in `src/rag/policy_docs/` into a retrieval collection, using file contents as-is with no content rewriting.
- **FR-002**: System MUST assign `policy_category` metadata to each chunk using the existing "Policy Category" header field in each source file.
- **FR-003**: System MUST assign `source_document` metadata to each chunk using the originating filename.
- **FR-004**: System MUST use `all-MiniLM-L6-v2` embeddings consistently for both ingestion and query-time retrieval.
- **FR-005**: System MUST chunk documents conservatively by section or paragraph boundaries so retrieved content remains coherent and complete.
- **FR-006**: System MUST add an `answer_policy_question` node that retrieves the top 3 relevant chunks for policy-question requests.
- **FR-007**: System MUST route `policy_question` intent to the `answer_policy_question` node instead of the placeholder response path.
- **FR-008**: System MUST instruct generation to answer only from retrieved context and explicitly state information is unavailable when context does not answer the question.
- **FR-008A**: System MUST append source provenance using `source_document` filename(s) in the final policy answer text.
- **FR-009**: System MUST skip generation and return a fixed no-information response when no retrieved chunk meets relevance threshold.
- **FR-009A**: System MUST treat retrieved chunks as usable context only when relevance score is at least 0.35.
- **FR-009B**: System MUST use the exact fallback response text `I don't have information on that policy.` when no retrieved chunk meets the threshold.
- **FR-010**: System MUST preserve stream contract for successful policy answers as `intent` then `token` content then `done`.
- **FR-011**: System MUST preserve generation-failure stream contract as `intent` then `error` with no `done` when generation fails after retrieval.
- **FR-012**: System MUST preserve all existing stage-1, stage-2, and stage-3 non-policy behavior and regression contracts.
- **FR-013**: System MUST treat the following as out of scope for this slice: password reset tool, ticket creation tool, PII redaction, prompt injection detection, long-term memory, Arize Phoenix instrumentation, Promptfoo evaluation, React frontend.

### Key Entities *(include if feature involves data)*

- **PolicyDocument**: One existing markdown policy source file from `src/rag/policy_docs/`, including header fields and body text.
- **PolicyChunk**: Coherent section or paragraph chunk derived from a PolicyDocument and stored with `policy_category` and `source_document` metadata.
- **RetrievalResult**: Ranked chunk set returned for a policy question, including relevance scores and metadata used for grounding decisions.
- **PolicyAnswerState**: Agent state subset for policy answering containing question text, retrieved context, decision on threshold pass/fail, and final answer or error outcome.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of contract-test policy questions clearly answerable from one policy document produce grounded answers containing only facts present in that document.
- **SC-002**: 100% of policy questions with no chunks above relevance threshold return the fixed no-information response and do not invoke generation.
- **SC-003**: 100% of policy questions spanning two categories return a grounded answer derived from retrieved multi-category context.
- **SC-004**: 100% of generation failures in the policy-answer path produce stream sequence `intent` then `error` with no `done`.
- **SC-005**: 100% of existing stage-1/stage-2/stage-3 regression tests continue to pass unchanged.

## Assumptions

- The five named policy documents already exist and include a usable "Policy Category" header field.
- Conservative section/paragraph chunking yields enough semantic completeness for retrieval without aggressive fixed-size splitting.
- The selected local embedding model is available for local execution without external API credentials.
- The selected local generation model is available in the runtime environment for policy-answer generation calls.
- Relevance threshold is configured at a level that prefers safe no-information fallback over low-confidence answers.
