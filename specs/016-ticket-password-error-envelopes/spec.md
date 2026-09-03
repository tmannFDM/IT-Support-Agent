# Feature Specification: Ticket Password Error Envelopes

**Feature Branch**: `[016-ticket-password-error-envelopes]`

**Created**: 2026-09-03

**Status**: Draft

**Input**: Correct the remaining ticket-creation and password-reset error-event payloads so they use the established error envelope and always provide a non-empty message.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Receive Safe Ticket Creation Errors (Priority: P1)

Support users need clear, non-empty errors when a ticket cannot be categorized or the ticket-creation action fails. The chat must remain usable, preserve the existing helpful category guidance, and communicate failures in the same structured form used by other error events.

**Why this priority**: Ticket creation is a core support flow. A plain-string error breaks the established frontend error contract and can cause a user-visible failure instead of a recoverable explanation.

**Independent Test**: Submit a ticket request without recognizable category detail and simulate a ticket-creation action exception; each stream emits an action-request intent followed by one parseable error envelope, no tool call, and no completion event.

**Acceptance Scenarios**:

1. **Given** a ticket request has no recognizable category, **When** the request is handled, **Then** the stream emits `action_request` followed by an error envelope with `ERR-TICKET-CATEGORY-REQUIRED` and the existing message asking for enough detail to categorize the ticket, with no tool-call or completion event.
2. **Given** ticket creation raises an exception with a message, **When** the failure is handled, **Then** the stream emits `action_request` followed by an error envelope with `ERR-TICKET-CREATE-FAILED` and a non-empty message, with no tool-call or completion event.
3. **Given** ticket creation raises an exception without a message, **When** the failure is handled, **Then** the error envelope contains a non-empty message naming the exception type and indicating that no message was provided.

---

### User Story 2 - Receive Safe Password Reset Errors (Priority: P1)

Support users need a clear, non-empty error if a validated password-reset action fails. The user must receive the established structured error outcome rather than a blank or malformed message.

**Why this priority**: Password reset is a high-impact access-recovery flow. Reliable failure messaging allows a user to understand that the request did not complete and seek the appropriate next step.

**Independent Test**: Simulate a password-reset action exception after a valid request; the stream emits an action-request intent followed by one parseable `ERR-PASSWORD-RESET-FAILED` error envelope and no completion event.

**Acceptance Scenarios**:

1. **Given** a valid password-reset request reaches the action, **When** the action raises an exception with a message, **Then** the stream emits `action_request` followed by an error envelope with `ERR-PASSWORD-RESET-FAILED` and a non-empty message, with no tool-call or completion event.
2. **Given** the password-reset action raises an exception without a message, **When** the failure is handled, **Then** the error envelope contains a non-empty message naming the exception type and indicating that no message was provided.
3. **Given** a password-reset action succeeds or escalates under existing rules, **When** its stream is handled, **Then** its existing tool-call, response, and completion behavior remains unchanged.

### Edge Cases

- The ticket category cannot be inferred; the existing helpful category guidance remains the error message inside the new envelope.
- A ticket-creation or password-reset exception has an empty string representation; the error message identifies its type and includes a no-message indication.
- A tool exception happens after intent classification; the stream remains `intent`, then `error`, with no tool-call or completion event.
- Existing success and password-reset escalation paths remain unaffected by this error-only correction.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST represent a ticket request with no recognizable category as an error envelope containing `ERR-TICKET-CATEGORY-REQUIRED` and the existing category-guidance message.
- **FR-002**: The system MUST represent every ticket-creation action exception as an error envelope containing `ERR-TICKET-CREATE-FAILED` and a non-empty message.
- **FR-003**: The system MUST represent every password-reset action exception as an error envelope containing `ERR-PASSWORD-RESET-FAILED` and a non-empty message.
- **FR-004**: When a caught ticket-creation or password-reset exception has no message, the system MUST use a fallback that includes the exception type name and a no-message indication.
- **FR-005**: The system MUST preserve the existing failure lifecycle for all three paths: action-request intent, then one error event, with no tool-call or completion event.
- **FR-006**: The system MUST preserve the existing ticket-creation success behavior and password-reset success and escalation behavior.
- **FR-007**: Existing tests for the three error paths MUST parse the error-event data as an envelope and verify the required code and a non-empty message rather than relying on plain-text data.

### Key Entities *(include if feature involves data)*

- **Error envelope**: A categorized failure payload containing `error_code` and a non-empty human-readable `message` in the existing error event data field.
- **Category guidance error**: The ticket-creation error shown when the request lacks enough information to determine a supported category.
- **Tool-action failure**: An exception raised while performing ticket creation or password reset after intent classification.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of category-missing ticket requests produce one `ERR-TICKET-CATEGORY-REQUIRED` error envelope containing the current category guidance and no tool-call or completion event.
- **SC-002**: 100% of simulated ticket-creation exceptions produce one `ERR-TICKET-CREATE-FAILED` error envelope with a non-empty message and no completion event.
- **SC-003**: 100% of simulated password-reset exceptions produce one `ERR-PASSWORD-RESET-FAILED` error envelope with a non-empty message and no completion event.
- **SC-004**: 100% of simulated silent tool exceptions produce a message containing the exception type name.
- **SC-005**: All existing chat-stream contract tests pass, including ticket-creation success and password-reset success/escalation flows.

## Assumptions

- The existing error event and its data field remain the transport for serialized error envelopes.
- The frontend's defensive error parser implemented in Feature 015 consumes these envelopes without any further frontend changes.
- This repair changes only the three identified error payloads and does not alter routing, tool invocation, event types, or completion behavior.
- The existing category-guidance wording remains user-approved and is preserved exactly.