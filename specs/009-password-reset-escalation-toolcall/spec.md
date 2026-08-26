# Feature Specification: Password Reset Escalation ToolCall Fix

**Feature Branch**: `[009-password-reset-escalation-toolcall]`

**Created**: 2026-08-26

**Status**: Draft

**Input**: User description: "Correct a bug in the password-reset escalation path so escalation metadata is emitted as structured tool_call data rather than leaked as raw field-name text in token output."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Structured Escalation Metadata in Stream (Priority: P1)

As a client consuming chat stream events, I want escalation outcomes represented as structured data in a tool_call event so I can parse escalation details reliably without scraping token text.

**Why this priority**: This directly fixes the reported production bug and restores stream-contract consistency between reset success and escalation outcomes.

**Independent Test**: Send suspicious password-reset requests and verify the event sequence includes intent, then tool_call containing a validated escalation payload, then token, then done.

**Acceptance Scenarios**:

1. **Given** a password-reset request escalated due to invalid employee ID, **When** stream events are emitted, **Then** the second content event is a tool_call carrying PasswordResetResponse with status `escalated` and escalation_reason `invalid_employee_id`.
2. **Given** a password-reset request escalated due to urgency pressure, **When** stream events are emitted, **Then** tool_call payload carries status `escalated` and escalation_reason `urgency_pressure`.
3. **Given** a password-reset request escalated due to vague reason, **When** stream events are emitted, **Then** tool_call payload carries status `escalated` and escalation_reason `vague_reason`.

---

### User Story 2 - Clean Human-Readable Escalation Token (Priority: P1)

As an end user, I want escalation messaging to be clear and human-readable so I do not see internal field names or key-value fragments in chat output.

**Why this priority**: The bug currently leaks internal formatting such as escalation_reason key fragments into user-visible tokens.

**Independent Test**: Trigger each escalation path and verify token text contains only human-readable language, without underscores-as-code, raw field keys, or key=value fragments.

**Acceptance Scenarios**:

1. **Given** an escalated password-reset outcome, **When** token content is emitted, **Then** the token message is a clean human-readable escalation explanation.
2. **Given** any escalated path, **When** tokens are emitted, **Then** tokens do not contain raw field-name literals such as escalation_reason, underscores-as-code fragments, or key=value formatting.

---

### User Story 3 - Preserve Existing Sequence and Prior Behavior (Priority: P2)

As a backend maintainer, I want the event sequence and existing non-bug behavior preserved so this change remains a targeted bug fix rather than a behavioral redesign.

**Why this priority**: The requested change is narrowly scoped; regressions in success path or prior stages would violate release safety.

**Independent Test**: Re-run existing password-reset and stage 1-5 contract tests, with escalation tests updated only for tool_call-before-token ordering.

**Acceptance Scenarios**:

1. **Given** a successful password-reset request, **When** stream events are emitted, **Then** success path remains intent, tool_call, token, done unchanged.
2. **Given** escalated password-reset requests, **When** stream events are emitted, **Then** sequence is intent, tool_call, token, done.
3. **Given** unexpected tool/runtime failure, **When** stream events are emitted, **Then** failure behavior remains intent, error, and no done.
4. **Given** non-password-reset flows (ticket status, RAG policy path, guardrail behavior), **When** tests run, **Then** those flows remain unchanged.

---

### Edge Cases

- A request matches multiple suspicion signals; tool_call escalation payload still carries exactly one reason selected by existing precedence, while token remains clean human-readable text.
- Escalation tool_call payload and token must remain logically consistent in the same response.
- If escalation payload serialization fails unexpectedly, existing error path behavior remains authoritative.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST represent escalated password-reset outcomes as a validated PasswordResetResponse payload emitted through a tool_call stream event.
- **FR-002**: System MUST include `employee_id`, `status`, `temporary_password_note`, and `escalation_reason` in the escalated tool_call payload.
- **FR-003**: System MUST set escalated payload status to `escalated` and escalation_reason to one of `invalid_employee_id`, `urgency_pressure`, or `vague_reason` per existing precedence rules.
- **FR-004**: System MUST emit a human-readable token message after escalation tool_call data.
- **FR-005**: System MUST NOT include raw internal field names, underscores-as-code fragments, or key=value pairs in escalation token text.
- **FR-006**: System MUST preserve event ordering for escalations as intent, tool_call, token, done.
- **FR-007**: System MUST preserve existing success-path ordering and payload behavior for `reset_issued` outcomes.
- **FR-008**: System MUST preserve existing failure-path behavior (intent, error, no done) for unexpected runtime/tool failures.
- **FR-009**: System MUST update existing password-reset escalation contract tests to assert tool_call precedes token on invalid ID, urgency pressure, and vague reason scenarios.
- **FR-010**: System MUST keep ticket-status routing behavior, RAG pipeline behavior, and guardrail (PII redaction/injection detection) behavior unchanged.
- **FR-011**: System MUST treat this scope as a bug fix and avoid introducing unrelated feature expansions.

### Key Entities *(include if feature involves data)*

- **EscalatedPasswordResetResponse**: Structured escalation payload using the existing PasswordResetResponse schema with status `escalated` and one valid escalation_reason.
- **EscalationUserTokenMessage**: Human-readable token content presented to users after tool_call emission with no internal key leakage.
- **PasswordResetEscalationStreamOutcome**: Event sequence contract for escalated outcomes: intent -> tool_call -> token -> done.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of escalated password-reset scenarios emit a tool_call event containing a valid escalated PasswordResetResponse before token emission.
- **SC-002**: 0 escalation token events include raw field-name leakage patterns (such as escalation_reason, underscores-as-code, or key=value fragments).
- **SC-003**: 100% of the four password-reset scenarios (valid reset, invalid ID escalation, urgency-pressure escalation, vague-reason escalation) pass with expected event order assertions.
- **SC-004**: Existing stage 1-5 contract/regression tests remain passing with no behavioral changes outside this bug fix.

## Assumptions

- The existing PasswordResetResponse schema remains the authoritative payload contract for both reset_issued and escalated outcomes.
- Escalation-reason precedence logic is already correct and remains unchanged in this slice.
- No new event types are required; this fix only changes escalation content event composition.
- Existing route-level stream formatter already supports tool_call emission and can be reused.
