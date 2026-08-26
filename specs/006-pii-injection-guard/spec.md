# Feature Specification: PII Redaction and Prompt Injection Guard

**Feature Branch**: `[006-pii-injection-guard]`

**Created**: 2026-08-26

**Status**: Draft

**Input**: User description: "Extend the IT Support Ticketing System with the fifth vertical slice: PII redaction and prompt injection detection, applied as middleware before any message reaches an LLM or the RAG pipeline."

## Clarifications

### Session 2026-08-26

- Q: For blocked prompt-injection responses, how should the stream carry the required ERR-PROMPT-INJECTION-BLOCKED code while keeping the existing event envelope? -> A: Keep `event_type: error` and put a JSON-encoded object string in `data` with `error_code` and generic `message`.
- Q: What exact generic blocked-message text should be returned for ERR-PROMPT-INJECTION-BLOCKED so tests and client behavior stay deterministic? -> A: Request blocked for safety.
- Q: Should prompt-injection keyword matching be case-insensitive and applied after trimming whitespace and collapsing repeated spaces? -> A: Yes, use case-insensitive matching with whitespace normalization before pattern checks.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Protect Sensitive User Data Before Processing (Priority: P1)

As an IT support user, I want sensitive details in my message to be masked before processing so my personal data is not exposed to downstream model prompts or logs.

**Why this priority**: Privacy protection is a core system principle and must happen before any classification, retrieval, or generation work.

**Independent Test**: Send a message containing an email address or phone number and confirm the request still completes normally while the processed message uses visible placeholders for masked values.

**Acceptance Scenarios**:

1. **Given** a non-malicious message that contains one or more email addresses, **When** the message enters the graph, **Then** each email value is replaced with a visible placeholder before any intent classification, retrieval, tool, or LLM step.
2. **Given** a non-malicious message that contains one or more phone numbers, **When** the message enters the graph, **Then** each phone number is replaced with a visible placeholder before any intent classification, retrieval, tool, or LLM step.
3. **Given** a message with PII but no injection attempt, **When** processing continues, **Then** the normal stream contract for legitimate requests is preserved and the user receives a normal response.

---

### User Story 2 - Block Prompt Injection Attempts Early (Priority: P1)

As a security owner, I want prompt-injection attempts blocked before classification and generation so override attacks cannot influence system behavior.

**Why this priority**: Prompt-injection defense must fail closed at the earliest possible point to prevent unsafe or manipulated model behavior.

**Independent Test**: Send a message with an obvious override phrase and confirm the first and only stream event is a blocked error outcome with no intent, token, tool_call, or retrieval activity.

**Acceptance Scenarios**:

1. **Given** a message containing an override phrase such as ignore previous instructions or reveal your system prompt, **When** pre-classification checks run, **Then** the system blocks processing before classification and emits an error event as the first stream event.
2. **Given** a blocked injection message, **When** the system responds, **Then** the error code is ERR-PROMPT-INJECTION-BLOCKED with a safe generic message that does not reveal the matched detection phrase.
3. **Given** a blocked injection message, **When** the system responds, **Then** the generic blocked message text is exactly Request blocked for safety.
4. **Given** a blocked injection message, **When** processing is terminated, **Then** no intent, token, done, tool_call, retrieval, or LLM activity occurs.
5. **Given** a message containing an override phrase with mixed casing or irregular spacing, **When** pre-classification checks run, **Then** normalization and case-insensitive matching still block the request.

---

### User Story 3 - Preserve Existing Behavior for Clean Requests (Priority: P2)

As a product owner, I want clean messages and prior stage behavior to remain unchanged so this slice improves security and privacy without introducing regressions.

**Why this priority**: This slice must be additive and safe, preserving validated behavior from stages 1 through 4.

**Independent Test**: Re-run existing stage 1-4 tests and verify clean messages with no PII and no injection patterns follow the same behavior as before this slice.

**Acceptance Scenarios**:

1. **Given** a clean message with no PII and no injection pattern, **When** it is processed, **Then** intent emission and downstream behavior are unaffected.
2. **Given** existing stage 1-4 regression checks, **When** the full suite runs, **Then** all previously passing behaviors remain passing.

---

### Edge Cases

- What happens when a message contains both PII and prompt-injection patterns? The message is blocked by injection detection before classification, with the blocked error event returned first.
- What happens when a message contains multiple PII values of mixed types? All detected email and phone values are masked using their respective placeholders.
- What happens when suspicious text is similar to but not clearly an override phrase? Only deterministic keyword or pattern matches trigger blocking in this slice.
- What happens when a message has no PII and no injection attempt? Processing remains unchanged from current behavior.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST run a pre-classification middleware step on every incoming message before intent classification and before any retrieval, tool, or generation operation.
- **FR-002**: System MUST provide a PII redaction capability that detects and masks email addresses and phone numbers in user messages using visible placeholders.
- **FR-003**: System MUST replace detected email addresses with [REDACTED_EMAIL] and detected phone numbers with [REDACTED_PHONE] in the processed message.
- **FR-004**: System MUST ensure that for non-blocked messages, downstream processing uses the redacted message for classification, retrieval, generation prompts, and logging surfaces.
- **FR-005**: System MUST provide deterministic prompt-injection detection using keyword and pattern matching without using an additional model-based classification call.
- **FR-006**: System MUST detect override-attempt phrases including ignore previous instructions, ignore the above, reveal your system prompt, you are now, disregard your instructions, and equivalent patterns.
- **FR-006A**: System MUST run prompt-injection matching case-insensitively after trimming whitespace and collapsing repeated spaces.
- **FR-007**: System MUST execute prompt-injection detection before intent classification so blocked messages never reach classification, retrieval, tool invocation, or LLM generation.
- **FR-008**: System MUST emit an error event as the first stream event for blocked messages, with error code ERR-PROMPT-INJECTION-BLOCKED and a safe generic message.
- **FR-008A**: System MUST keep the existing stream envelope and encode blocked-error details in the `error` event `data` field as a JSON object string containing `error_code` and generic `message`.
- **FR-008B**: System MUST use the exact generic blocked message text `Request blocked for safety.` for ERR-PROMPT-INJECTION-BLOCKED responses.
- **FR-009**: System MUST NOT emit intent, token, tool_call, or done events for blocked prompt-injection messages.
- **FR-010**: System MUST continue normal processing for messages that contain PII but no injection attempt, including standard intent-first behavior for legitimate requests.
- **FR-011**: System MUST leave clean messages with no PII and no injection attempt behaviorally unchanged.
- **FR-012**: System MUST preserve all existing stage 1-4 behavior and regression outcomes for prior intent paths.
- **FR-013**: System MUST treat as out of scope for this slice: password reset tool, ticket creation tool, long-term memory, Arize Phoenix instrumentation, Promptfoo evaluation, React frontend, and model-based injection classification.

### Key Entities *(include if feature involves data)*

- **MessageSafetyCheckResult**: Pre-classification decision bundle describing whether prompt injection was detected and what safe response should be emitted if blocked.
- **RedactionResult**: Processed message output containing masked placeholders and indicators of whether email and phone redaction were applied.
- **BlockedErrorOutcome**: Deterministic stream error outcome for prompt-injection messages, including the required error code and generic message.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of test messages containing email addresses or phone numbers and no injection pattern complete normal request processing with placeholders applied to downstream message content.
- **SC-002**: 100% of test messages containing explicit prompt-injection override patterns return ERR-PROMPT-INJECTION-BLOCKED as the first event with no intent, token, tool_call, or done events.
- **SC-003**: 100% of clean test messages with no PII and no injection pattern remain behaviorally unchanged from pre-slice baseline.
- **SC-004**: 100% of existing stage 1-4 regression tests continue to pass unchanged after this slice is implemented.

## Assumptions

- Existing stream envelope supports error events carrying structured safe error information required by this slice.
- Current logging and downstream processing points can consume the sanitized message value without requiring schema expansion.
- Deterministic phrase and pattern matching is sufficient for this vertical slice, with broader adaptive detection deferred to future work.
- The blocked response text should avoid pattern-specific disclosures and remain consistent across matched injection phrases.
