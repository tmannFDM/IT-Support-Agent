# Feature Specification: Error Envelope Fallback

**Feature Branch**: `[015-error-envelope-fallback]`

**Created**: 2026-09-03

**Status**: Draft

**Input**: Correct inconsistent generation-failure error payloads and ensure the chat interface safely displays malformed or empty error payloads.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Show Generation Failures Safely (Priority: P1)

Support users need a clear, non-empty error message when response generation fails so the chat remains usable and the failure can be understood without a blank response or application crash. Both direct-answer and policy-answer failures communicate a consistent error envelope while retaining their distinct failure categories.

**Why this priority**: A backend failure currently risks a malformed error event and can crash the chat interface. Safe, readable error handling preserves the core support experience during an operational failure.

**Independent Test**: Simulate a direct-response generation failure and a policy-answer generation failure; each stream contains an intent event followed by one error event with a non-empty message and contains no completion event.

**Acceptance Scenarios**:

1. **Given** direct response generation raises an exception with a message, **When** the failure is streamed, **Then** the stream sends the direct-response intent followed by an error event containing an error code of `ERR-LLM-GENERATION-FAILED` and the exception message, with no completion event.
2. **Given** policy answer generation raises an exception with a message, **When** the failure is streamed, **Then** the stream sends the policy-question intent followed by an error event containing an error code of `ERR-POLICY-GENERATION-FAILED` and the exception message, with no completion event.
3. **Given** either generation path raises an exception with no message, **When** the failure is streamed, **Then** the error event contains a non-empty message that names the exception type and indicates that no message was supplied.

---

### User Story 2 - Tolerate Invalid Error Events (Priority: P1)

Chat users need the interface to remain stable when an error event contains empty or invalid data, including data from an older or faulty backend. The interface presents a safe generic error message instead of crashing.

**Why this priority**: Error reporting must be most reliable when upstream systems are already failing. A malformed error event must not turn a recoverable service failure into a broken chat session.

**Independent Test**: Supply empty and non-JSON error event data to the frontend error parser and verify that each produces a defined fallback message without throwing.

**Acceptance Scenarios**:

1. **Given** an error event contains an empty data field, **When** the interface processes it, **Then** it returns a non-empty fallback error message and continues rendering.
2. **Given** an error event contains invalid JSON, **When** the interface processes it, **Then** it returns a non-empty fallback error message and continues rendering.
3. **Given** an error event contains a valid message envelope, **When** the interface processes it, **Then** it displays the supplied non-empty message.

### Edge Cases

- A caught exception has an empty string representation; the error message identifies its exception type and includes a no-message indication.
- An error event's data field is whitespace-only, malformed JSON, a JSON primitive, or an object missing a text message; the interface uses its generic fallback.
- A valid error envelope contains an empty message; the interface treats it as invalid and uses its generic fallback.
- A generation failure occurs after its intent was already emitted; the stream ends after the error event and does not emit a completion event.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST represent every direct-response generation exception as an error envelope containing `error_code` and a non-empty `message`.
- **FR-002**: The system MUST use `ERR-LLM-GENERATION-FAILED` as the error code for a direct-response generation exception.
- **FR-003**: The system MUST represent every policy-answer generation exception as an error envelope containing `error_code` and a non-empty `message`.
- **FR-004**: The system MUST use `ERR-POLICY-GENERATION-FAILED` as the error code for a policy-answer generation exception.
- **FR-005**: When a caught generation exception has no message, the system MUST provide a fallback message containing the exception type name and a no-message indication.
- **FR-006**: The system MUST keep the existing failure stream ordering: the applicable intent event, then one error event, with no completion event for either generation failure path.
- **FR-007**: The chat interface MUST parse empty, invalid, or structurally invalid error-event data without throwing.
- **FR-008**: For an invalid error payload, the chat interface MUST provide a non-empty, user-safe fallback message.
- **FR-009**: For a valid error payload with a non-empty message, the chat interface MUST display that message.
- **FR-010**: Existing generation-failure tests MUST verify an error event is emitted with a non-empty message and MUST not depend on the superseded error-code values.

### Key Entities *(include if feature involves data)*

- **Error envelope**: A failure event payload with an error category (`error_code`) and non-empty human-readable explanation (`message`).
- **Generation failure**: An exception raised while producing a direct response or a policy-grounded response.
- **Fallback error message**: A stable non-empty message used when an incoming error payload cannot be safely interpreted.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of simulated direct-response generation failures produce one error event with `ERR-LLM-GENERATION-FAILED`, a non-empty message, and no completion event.
- **SC-002**: 100% of simulated policy-answer generation failures produce one error event with `ERR-POLICY-GENERATION-FAILED`, a non-empty message, and no completion event.
- **SC-003**: 100% of simulated empty-message exceptions produce an error message containing the exception type name.
- **SC-004**: 100% of tested empty, malformed, and structurally invalid error payloads are rendered with a non-empty fallback message without a frontend exception.
- **SC-005**: All existing chat-stream contract tests continue to pass after the change.

## Assumptions

- The existing error-event data field remains the cross-layer location for the serialized error envelope.
- The existing user-facing generic error fallback remains appropriate for malformed error payloads.
- This repair does not introduce new event types or alter successful streaming behavior.
- The generation-failure tests will be updated only to validate the documented non-empty error-message contract and new failure categories.