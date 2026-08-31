# Phase 0 Research: In-Session Conversation History Window

## Decision 1: Session-scoped in-memory store keyed by session_id
- Decision: Implement short-term history as a process-local in-memory store in `src/agent/` keyed by `session_id`, separate from long-term per-user JSON memory.
- Rationale: Matches explicit requirement for ephemeral, restart-volatile behavior and avoids coupling to durable user profile memory.
- Alternatives considered:
  - Reuse long-term `src/memory/store.py`: rejected because durability and user_id semantics violate session-scoped requirement.
  - External datastore (Redis/DB): rejected as out of scope and unnecessary complexity for this slice.

## Decision 2: Fixed sliding window of 5 completed exchanges
- Decision: Enforce a strict max of 5 exchanges per session and evict oldest-first when a 6th exchange is appended.
- Rationale: Directly satisfies NFR-006 bounded context/token growth and specified acceptance behavior.
- Alternatives considered:
  - Token-count-based dynamic window: rejected for this pass due added estimation complexity.
  - Unbounded list: rejected due NFR violation.

## Decision 3: Store redacted text only for both user and assistant turns
- Decision: Persist only redacted message/response text in session history entries.
- Rationale: Aligns with accepted clarification and constitution privacy constraints.
- Alternatives considered:
  - Store raw text and redact on retrieval: rejected due elevated leakage risk.
  - Dual raw+redacted storage: rejected as unnecessary for this scope and riskier.

## Decision 4: Append history only after request completion (`done` path)
- Decision: Record the exchange only after successful response completion for that request.
- Rationale: Prevents partial/incomplete turn capture and matches explicit acceptance criteria.
- Alternatives considered:
  - Append before streaming tokens: rejected because failures/disconnects could store incomplete assistant outputs.
  - Append at graph node boundaries: rejected because done-event completion semantics are owned by stream flow.

## Decision 5: Inject session history only into direct and policy LLM prompt construction
- Decision: Extend direct-response and policy-response LLM message assembly to prepend recent session turns when available.
- Rationale: Delivers follow-up continuity where requested while minimizing unintended behavior shifts.
- Alternatives considered:
  - Inject history into every intent path: rejected because tool paths must remain history-independent this pass.
  - Keep history unused in prompts: rejected because it fails the primary user story.

## Decision 6: Keep tool-invoking extraction/routing paths unchanged
- Decision: Preserve ticket-status, password-reset, and ticket-creation extraction/routing logic exactly as current-message-only processing.
- Rationale: Explicit scope boundary and regression-risk control from spec and user instructions.
- Alternatives considered:
  - Thread history through extraction helpers: rejected as out of scope and likely to alter deterministic behavior.

## Decision 7: Add contract tests that validate behavior through captured LLM payloads
- Decision: Add contract tests that monkeypatch LLM-call functions to capture constructed message payloads and assert same-session continuity, isolation, bounded eviction, and tool-path invariance.
- Rationale: Verifies prompt-context behavior directly and protects existing slices from regressions.
- Alternatives considered:
  - Output-only assertions without payload capture: rejected because they do not prove context injection mechanics.
