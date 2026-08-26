# Phase 0 Research: Password Reset Escalation ToolCall Fix

## Decision 1: Emit structured escalation data as tool_call using existing PasswordResetResponse contract
- Decision: For escalated password-reset outcomes, produce JSON tool_call payload containing employee_id, status, temporary_password_note, and escalation_reason.
- Rationale: Fixes field-name leakage bug and aligns escalation with success-path structured event behavior.
- Alternatives considered:
  - Keep escalation metadata in token text: rejected because it is brittle and leaks internal key formatting.
  - Introduce a new event type for escalation: rejected as unnecessary contract expansion.

## Decision 2: Keep token strictly human-readable after escalation tool_call
- Decision: Token message remains plain explanatory text without raw field names, underscore identifiers, or key=value fragments.
- Rationale: User-facing output should not expose internal serialization details.
- Alternatives considered:
  - Include debug-oriented reason fragments in token text: rejected due to UX and leakage concerns.

## Decision 3: Preserve sequence and failure semantics
- Decision: Escalation path sequence is intent -> tool_call -> token -> done; existing failure semantics remain intent -> error -> no done.
- Rationale: This is a bug fix, not a behavior redesign.
- Alternatives considered:
  - Collapse escalation into tool_call-only output: rejected because human-readable token is still required.

## Decision 4: Keep scope limited to node and stream-emitter surfaces
- Decision: Modify check_password_reset in src/agent/nodes.py and use src/api/routes/chat.py only if needed for tool_call emission.
- Rationale: Meets explicit user constraints and minimizes regression risk.
- Alternatives considered:
  - Add new schemas/tools/helpers: rejected because existing PasswordResetResponse already satisfies data needs.

## Decision 5: Update escalation contract tests for event ordering
- Decision: Update existing invalid-ID, urgency-pressure, and vague-reason tests to assert tool_call precedes token.
- Rationale: Ensures the bug fix is locked by automated checks without altering success-path expectations.
- Alternatives considered:
  - Only manual verification: rejected due to regression risk.
