# Phase 0 Research: Password Reset Tool Slice

## Decision 1: Introduce a dedicated FastMCP password_reset tool with schema-first IO
- Decision: Add a dedicated tool entrypoint for password reset handling with strict request/response schemas.
- Rationale: Aligns with constitution requirement for schema-validated tooling and avoids implicit payload parsing.
- Alternatives considered:
  - Reuse generic action_request placeholder branch: rejected because it cannot represent tool outcomes or escalation metadata deterministically.
  - Implement reset directly in route layer: rejected because it bypasses tool contract boundaries.

## Decision 2: Use mocked in-memory reset behavior with fixed temporary-password note
- Decision: Tool returns deterministic mocked outcome and fixed note: "A temporary password has been issued and will be required to be changed on next login."
- Rationale: Meets feature scope while explicitly avoiding real password generation/exposure.
- Alternatives considered:
  - Integrate real identity backend: rejected as out of scope for this slice.
  - Generate random placeholder passwords: rejected due to policy requirement to never expose actual password values.

## Decision 3: Implement deterministic suspicion checks before any tool call
- Decision: Apply suspicion checks in password-reset node using three signals: invalid employee ID, urgency pressure, and vague reason.
- Rationale: Mirrors existing fail-safe-over-guessing principle and password policy guidance.
- Alternatives considered:
  - Attempt reset first then evaluate response: rejected because risky actions must be prevented before execution.
  - Score-based probabilistic decisioning: rejected due to lower test determinism and unnecessary complexity.

## Decision 4: Define exact precedence for multi-signal suspicious requests
- Decision: Return exactly one escalation reason using precedence invalid_employee_id > urgency_pressure > vague_reason.
- Rationale: Prevents ambiguous responses and flakey tests when multiple signals are present.
- Alternatives considered:
  - Return all reasons: rejected because output contract expects one deterministic reason for this slice.
  - First-match-by-implementation-order: rejected due to unstable behavior across refactors.

## Decision 5: Reuse normalization strategy from injection detection for urgency matching
- Decision: Normalize casing/whitespace in password-reset suspicion checks using the same matching style as stage-5 injection detection.
- Rationale: Keeps text matching behavior predictable and consistent across safety checks.
- Alternatives considered:
  - Regex-heavy NLP matching: rejected as unnecessary for scoped keyword checks.

## Decision 6: Preserve stream contract and existing stage behavior
- Decision: Maintain event ordering and failure semantics; only password-reset-specific action requests branch to the new node.
- Rationale: Limits regression risk in stage 1-5 behavior and preserves existing external contract.
- Alternatives considered:
  - Redesign event envelope for tool metadata: rejected as out of scope and backward-incompatible.
