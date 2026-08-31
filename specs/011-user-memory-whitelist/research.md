# Phase 0 Research: Long-Term User Memory Whitelist

## Decision 1: Use JSON-file-backed storage in src/memory/
- Decision: Persist whitelist user facts in a local JSON file keyed by user_id (for example `src/memory/user_memory.json`) with a small read/write module.
- Rationale: Meets clarified requirement for lightweight persistence that survives restart without introducing a full database.
- Alternatives considered:
  - SQLite file: rejected due to clarification selecting JSON for MVP.
  - In-memory dict: rejected because it loses data on restart.

## Decision 2: Closed schema whitelist for persisted facts
- Decision: Define `UserMemoryFacts` with only `preferred_device_type`, `office_region`, and `timezone` as optional literal-constrained fields.
- Rationale: Enforces hard privacy boundaries and prevents accidental open-ended profile storage.
- Alternatives considered:
  - Generic key-value memory: rejected as explicitly out of scope and high privacy risk.

## Decision 3: Deterministic pattern extraction per field
- Decision: Implement independent keyword/pattern matching checks for each field and allow partial updates where valid fields persist and invalid candidates are ignored.
- Rationale: Matches project pattern-first approach, avoids LLM extraction, and aligns with accepted clarification semantics.
- Alternatives considered:
  - Single-pass all-or-nothing extraction: rejected because it would discard valid facts unnecessarily.
  - LLM extraction: rejected by scope and determinism constraints.

## Decision 4: Execute extraction after redaction in guardrail flow
- Decision: Run memory extraction after PII redaction within or alongside `guardrail_check_node` before intent classification.
- Rationale: Preserves privacy principle and ensures memory capture reads sanitized content.
- Alternatives considered:
  - Extract before redaction: rejected because it risks persisting sensitive data.
  - Extract in downstream intent nodes: rejected because it duplicates logic and misses intent-agnostic capture requirement.

## Decision 5: Optional fact enrichment for relevant nodes only
- Decision: Load stored facts by user_id and make them available to at least `generate_response_node` and `answer_policy_question_node`; never require them for response completion.
- Rationale: Supports natural context reuse without blocking baseline functionality.
- Alternatives considered:
  - Mandatory memory dependency for responses: rejected because absence must never block.
  - No readback integration: rejected because it fails cross-session utility objective.

## Decision 6: Keep non-target feature behavior unchanged
- Decision: Limit edits to memory module, schemas, minimal agent wiring, and contract tests; avoid ticket/password-reset/RAG/guardrail semantic changes.
- Rationale: Reduces regression risk and follows explicit scope boundaries.
- Alternatives considered:
  - Broad refactors while touching agent flow: rejected as out of scope.

## Decision 7: Contract-test coverage mirrors acceptance criteria
- Decision: Add contract tests for cross-session retrieval with same user_id, partial-valid storage, restart persistence, and no-memory-content behavior equivalence.
- Rationale: Ensures measurable acceptance proof and protects prior stage behavior.
- Alternatives considered:
  - Manual spot checks only: rejected due to weak regression protection.
