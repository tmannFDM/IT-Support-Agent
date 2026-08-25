# Phase 0 Research: Chat Stream Vertical Slice

## Decision 1: Backend runtime and framework
- Decision: Use Python 3.11+ with FastAPI and Pydantic v2 for the MVP backend slice.
- Rationale: Matches requested runtime baseline, provides first-class async support, and enforces schema-first boundary validation.
- Alternatives considered:
  - Flask + marshmallow: simpler routing but weaker integrated async/SSE ergonomics.
  - Django REST Framework: too heavy for an MVP transport slice.

## Decision 2: SSE transport shape
- Decision: Implement `/chat/stream` as an SSE endpoint that emits `ChatStreamEvent` payloads with `event_type` and `data`, producing at minimum `token` then `done` for valid requests.
- Rationale: Satisfies acceptance criteria while keeping the response deterministic and independent of LLM integrations.
- Alternatives considered:
  - WebSocket: bidirectional but unnecessary complexity for one-way stream proof.
  - Chunked plain text: weaker contract clarity for clients.

## Decision 3: Validation error contract
- Decision: Normalize missing or empty required-field validation failures to include machine-readable code `ERR-VALIDATION-MISSING-FIELD`.
- Rationale: Creates stable consumer behavior for contract tests and downstream UI handling.
- Alternatives considered:
  - Raw framework validation payloads only: less stable over framework version changes.
  - Single generic error code: loses precision for required input failures.

## Decision 4: Scope boundaries for this pass
- Decision: Implement only `src/api/`, `src/schemas/`, and `tests/`; explicitly defer agent, RAG, tools, security, and observability modules.
- Rationale: Aligns with vertical-slice plumbing goal and avoids speculative architecture before transport contracts are proven.
- Alternatives considered:
  - Stub all future modules now: adds churn and fake complexity without immediate value.

## Decision 5: Test strategy
- Decision: Add contract tests for `/chat/stream` and `/health` only, covering happy path and required validation failure.
- Rationale: Directly maps to acceptance criteria and gives fast feedback before broader functionality exists.
- Alternatives considered:
  - Full integration/e2e suite with external services: premature for this no-intelligence slice.
  - Unit-only tests: insufficient confidence in wire-level behavior.

## Clarifications Resolved
- No LLM call is needed for this pass; stream data may be echoed or hardcoded.
- `ChatStreamEvent` keeps enum values `token`, `tool_call`, `error`, `done` at schema level; this slice emits only `token` and `done` during successful flow.
- `/health` response includes service status and version with HTTP 200.
