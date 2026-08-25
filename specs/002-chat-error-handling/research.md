# Phase 0 Research: Chat Error Handling Baseline

## Decision 1: Runtime and framework baseline
- Decision: Use Python 3.11+ with FastAPI and Pydantic v2.
- Rationale: Matches requested backend version floor and enables schema-first validation at API boundaries.
- Alternatives considered:
  - Flask + manual validation: simpler stack but weaker built-in request validation consistency.
  - Django REST Framework: heavier than needed for this MVP slice.

## Decision 2: Validation failure contract
- Decision: Return HTTP 422 for missing, empty, and whitespace-only required chat fields with payload keys `error_code` and `message`, optional `details`.
- Rationale: Stable client contract, aligned with clarified requirements and acceptance testing.
- Alternatives considered:
  - HTTP 400 mapping: less aligned with validation semantics.
  - Variable payload shapes: brittle for consumers and tests.

## Decision 3: Details list structure
- Decision: When present, `details` includes all invalid required fields using `{ "field": "<name>", "issue": "<reason>" }`.
- Rationale: Deterministic parsing and complete correction feedback in one response.
- Alternatives considered:
  - First-error only: increases client retry cycles.
  - Field names only: insufficiently descriptive for users.

## Decision 4: Disconnect behavior
- Decision: On client disconnect during stream, stop generation immediately, do not retry, and emit no further events.
- Rationale: Conserves resources, avoids ambiguous post-disconnect behavior, and keeps stream lifecycle deterministic.
- Alternatives considered:
  - Retry or resume stream: adds complexity outside current scope.
  - Continue generation after disconnect: wastes compute and may leak stale state.

## Decision 5: Pass scope boundaries
- Decision: Build only `src/api/`, `src/schemas/`, and `tests/`, with contract tests for `/chat/stream` and `/health`.
- Rationale: Preserves vertical-slice discipline and avoids premature expansion.
- Alternatives considered:
  - Stubbing agent/rag/tools/security/observability now: introduces unused complexity.

## Clarifications Resolved
- Whitespace-only inputs are trimmed then validated; empty-after-trim is invalid.
- Validation failures for this pass always use HTTP 422 + `ERR-VALIDATION-MISSING-FIELD`.
- Error payload shape is stable: `error_code`, `message`, optional `details` with fixed item schema.
- Disconnect handling is immediate stop, no retry, no further events.
