# Feature Specification: Password Reset Tool Slice

**Feature Branch**: `[008-password-reset-tool-slice]`

**Created**: 2026-08-26

**Status**: Draft

**Input**: User description: "Extend the IT Support Ticketing System with the sixth vertical slice: a FastMCP password reset tool, replacing the placeholder response for password-reset action_requests."

## Clarifications

### Session 2026-08-26

- Q: What employee ID format should be treated as valid for password reset requests? → A: EMP- followed by 4 digits (for example EMP-1234).
- Q: Which exact escalation_reason values should the system use in responses for suspicious password-reset requests? → A: Use exactly vague_reason, urgency_pressure, invalid_employee_id.
- Q: How should the system classify a reason as too vague for auto-reset approval? → A: Vague if reason (normalized) matches or reduces to one of: reset my password, need password reset, forgot my password, please reset it, password reset, need a reset. Any reason containing detail beyond these phrases is not vague.
- Q: If a request triggers more than one suspicion rule, which single escalation_reason should be returned? → A: Precedence is invalid_employee_id, then urgency_pressure, then vague_reason.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Complete Password Reset Flow (Priority: P1)

As an employee with a locked or forgotten password, I want a clear request path that can issue a reset when my request includes the required identity and business reason details.

**Why this priority**: This is the core user value for the sixth vertical slice and replaces a placeholder path with a functional ticketing-safe outcome.

**Independent Test**: Submit a well-formed password reset request with a valid employee ID and specific reason, then verify the stream emits intent, tool call result, confirmation token, and done.

**Acceptance Scenarios**:

1. **Given** a password-reset request containing a valid employee ID and a specific reason, **When** the request is processed, **Then** the system classifies it as password-reset handling and emits `intent` first.
2. **Given** a request that passes suspicion checks, **When** reset handling continues, **Then** the system emits a `tool_call` event containing a `reset_issued` result and a note that a temporary password was issued and must be changed at next login.
3. **Given** a successful password reset tool outcome, **When** stream output is completed, **Then** the system emits a user-facing confirmation `token` followed by `done`.

---

### User Story 2 - Fail-Safe Escalation for Suspicious Requests (Priority: P1)

As a security owner, I want suspicious password-reset requests escalated to a human agent so the system avoids unsafe automated reset actions.

**Why this priority**: Fail-safe escalation protects account security and follows the existing stage-3 policy of escalating uncertain or risky requests.

**Independent Test**: Submit password-reset messages with missing/malformed employee ID, vague/missing reason, and urgency-pressure language; verify escalation is returned as normal token output without tool execution.

**Acceptance Scenarios**:

1. **Given** a password-reset request where reason is missing or normalizes to one of the fixed generic phrases (`reset my password`, `need password reset`, `forgot my password`, `please reset it`, `password reset`, `need a reset`), **When** suspicion checks run, **Then** the request is escalated with `escalation_reason` set to `vague_reason` and no reset tool call.
2. **Given** a password-reset request containing urgency-pressure language such as immediate or coercive urgency phrasing, **When** suspicion checks run, **Then** the request is escalated with `escalation_reason` set to `urgency_pressure` and no reset tool call.
3. **Given** a password-reset request with missing or malformed employee ID, **When** suspicion checks run, **Then** the request is escalated with `escalation_reason` set to `invalid_employee_id` and no reset tool call.
4. **Given** a suspicious request, **When** stream output is produced, **Then** the sequence is `intent` then escalation `token` then `done` and never an `error` event.
5. **Given** an employee ID not matching `EMP-1234` format, **When** suspicion checks run, **Then** the request is escalated with an identity-quality escalation reason and no reset tool call.
6. **Given** a request that matches more than one suspicion rule, **When** escalation reason is selected, **Then** exactly one reason is returned using precedence `invalid_employee_id` then `urgency_pressure` then `vague_reason`.

---

### User Story 3 - Preserve Existing Stages and Contracts (Priority: P2)

As a backend maintainer, I want all existing stages (ticket-status routing, policy responses, and guardrails) to remain unchanged while adding this slice.

**Why this priority**: Regressions in previously validated stages would reduce confidence in vertical-slice delivery.

**Independent Test**: Run existing stage 1-5 contract and regression tests and verify their behavior is unchanged while password-reset requests use the new path.

**Acceptance Scenarios**:

1. **Given** a ticket-status request, **When** intent routing occurs, **Then** it remains on the existing ticket-status path and does not use password reset handling.
2. **Given** non-password action requests, **When** routed, **Then** they continue to follow their existing behavior unless explicitly classified as password-reset requests.
3. **Given** prompt-injection or privacy guardrail-triggering inputs, **When** requests are processed, **Then** existing guardrail behavior and contracts remain unchanged.
4. **Given** an unexpected password reset tool failure, **When** stream output is emitted, **Then** the pattern remains `intent` then `error` with no `done` event.

---

### Edge Cases

- A message contains password-reset keywords but includes no employee ID; escalation is returned as a normal outcome with an identity-related escalation reason.
- A message includes an employee ID and reason but also urgency-pressure language; urgency takes precedence and the request is escalated.
- A message appears to include a current password value; the request is still treated under normal routing and must not require or accept current-password verification in this slice.
- A request includes multiple intents (ticket status plus reset); password-reset-specific routing applies only when reset intent is clearly present, otherwise existing routing behavior remains.
- A request matches multiple suspicion signals at once; only one `escalation_reason` is returned using precedence `invalid_employee_id` then `urgency_pressure` then `vague_reason`.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST provide a password reset tool capability named `password_reset` that receives employee ID and reason fields.
- **FR-002**: System MUST validate reset-tool request payloads using a `PasswordResetRequest` schema with required fields `employee_id` and `reason`.
- **FR-003**: System MUST return reset-tool outcomes using a `PasswordResetResponse` schema containing `employee_id`, `status`, `temporary_password_note`, and optional `escalation_reason`.
- **FR-004**: System MUST constrain `status` values to `reset_issued` or `escalated`.
- **FR-005**: System MUST detect password-reset-specific requests from action-request messages (including keyword families such as reset password, forgot password, and locked out) and route them to a password-reset decision path distinct from ticket-status handling and generic placeholders.
- **FR-006**: System MUST perform suspicion checks before reset-tool execution.
- **FR-007**: System MUST mark requests as suspicious and escalate when reason is missing or normalizes to one of the fixed generic phrases `reset my password`, `need password reset`, `forgot my password`, `please reset it`, `password reset`, `need a reset`; reasons containing additional concrete detail beyond those phrases are not vague for this rule.
- **FR-008**: System MUST mark requests as suspicious and escalate when urgency-pressure language is detected.
- **FR-009**: System MUST treat employee ID as valid only when it matches `EMP-` followed by exactly 4 digits and MUST mark requests as suspicious and escalate when employee ID is missing or malformed.
- **FR-010**: System MUST NOT execute the password reset tool for suspicious requests.
- **FR-011**: System MUST return escalation as a normal non-error response with an explicit `escalation_reason` and MUST only use `vague_reason`, `urgency_pressure`, or `invalid_employee_id`.
- **FR-012**: If more than one suspicion rule matches, system MUST return exactly one `escalation_reason` using precedence `invalid_employee_id` then `urgency_pressure` then `vague_reason`.
- **FR-013**: System MUST return successful non-suspicious outcomes as `reset_issued` with a temporary-password note stating that a temporary password was issued and must be changed at next login, without exposing an actual password value.
- **FR-014**: System MUST preserve stream sequencing rules: `intent` first, then `tool_call` for successful reset or `token` for escalation, then `done`.
- **FR-015**: System MUST preserve existing unexpected-failure behavior: if tool execution fails unexpectedly, emit `intent` then `error` and omit `done`.
- **FR-016**: System MUST NOT ask for or accept a current/existing password as input for this slice.
- **FR-017**: System MUST keep stage 1-5 behavior unchanged, including ticket-status routing and current guardrail outcomes.
- **FR-018**: System MUST keep out of scope for this slice: ticket creation tool, long-term memory, Arize Phoenix instrumentation, Promptfoo evaluation, and React frontend work.

### Key Entities *(include if feature involves data)*

- **PasswordResetRequest**: Input entity containing employee identifier and business reason for reset processing.
- **PasswordResetResponse**: Outcome entity containing employee identifier, decision status (`reset_issued` or `escalated`), temporary password process note, and optional escalation reason constrained to `vague_reason`, `urgency_pressure`, or `invalid_employee_id` when present.
- **PasswordResetSuspicionAssessment**: Decision entity that captures whether escalation is required based on vague reason, urgency pressure, or employee-ID quality, including normalized phrase-list matching for the vague-reason condition and deterministic precedence for single-reason output.
- **PasswordResetStreamOutcome**: Stream-level outcome entity defining valid event ordering for success, escalation, and unexpected tool failure paths.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of well-formed password-reset requests with valid employee ID and specific reason return a `tool_call` with `reset_issued`, followed by confirmation token and `done`.
- **SC-002**: 100% of password-reset requests with vague/missing reason, urgency-pressure language, or missing/malformed employee ID return escalation via `token` (not `error`) and include an escalation reason.
- **SC-003**: 100% of successful reset responses state that a temporary password was issued and must be changed at next login, and never include an actual password value.
- **SC-004**: Existing stage 1-5 regression tests pass without behavioral changes to ticket-status routing, policy paths, and guardrail contracts.

## Assumptions

- Password policy guidance already defines when reset requests must be escalated; this feature applies those rules consistently.
- Employee ID format standards already exist in current organizational policy and are reused for malformed-ID checks.
- Employee IDs for this slice use the canonical format `EMP-` followed by exactly 4 digits.
- Existing stream envelope and event names remain authoritative and are not redesigned in this slice.
- Password-reset requests continue to be processed through the existing action-request flow with additional password-reset-specific routing.
- Password content detection is not expanded in this slice beyond the explicit rule that current/existing passwords are not accepted as reset input.
