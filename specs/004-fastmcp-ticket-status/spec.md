# Feature Specification: FastMCP Ticket Status Slice

**Feature Branch**: `[004-fastmcp-ticket-status]`

**Created**: 2026-08-25

**Status**: Draft

**Input**: User description: "Extend the IT Support Ticketing System with the third vertical slice: a real FastMCP tool for ticket status lookup, replacing the placeholder response for ticket-status requests."

## Clarifications

### Session 2026-08-25

- Q: What ticket ID format should the system recognize in user messages for status lookup? (FR-008) -> A: Accept IDs matching `TKT-<digits>` only, case-insensitive on the prefix.
- Q: How should the validated TicketStatusResponse be encoded in the tool_call event payload? (FR-012) -> A: Keep `data` as string and send TicketStatusResponse as JSON-serialized text in the `tool_call` event.
- Q: What format should last_updated use in TicketStatusResponse so clients can parse it consistently? (FR-003) -> A: Use UTC ISO 8601 with `Z` suffix only.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Retrieve Ticket Status via Tool (Priority: P1)

As an IT support user, I want ticket-status questions to return real ticket details from a validated tool so I can immediately understand progress on an existing ticket.

**Why this priority**: This is the core value of the slice and replaces a placeholder with a real end-to-end capability.

**Independent Test**: Can be fully tested by sending a ticket-status message containing a valid ticket ID and verifying the stream emits intent first, then a structured tool result, then a human-readable summary, then completion.

**Acceptance Scenarios**:

1. **Given** a ticket-status request that includes a valid existing ticket ID, **When** the request is streamed, **Then** events are emitted in order: `intent`, `tool_call` with validated ticket details, `token` with summary text, and `done`.
2. **Given** a ticket-status request for a valid-format but unknown ticket ID, **When** the request is streamed, **Then** the stream emits `intent`, then `token` indicating ticket not found, then `done`, and does not emit `error`.

---

### User Story 2 - Handle Missing Ticket ID Safely (Priority: P1)

As an IT support user, I want clear guidance when I ask for ticket status without a ticket ID so I can correct my request without receiving fabricated results.

**Why this priority**: Preventing guessed identifiers and unsafe tool calls is essential for trust and correctness.

**Independent Test**: Can be fully tested by sending a ticket-status request without an identifiable ticket ID and verifying an `error` event is returned after `intent`, with no tool invocation.

**Acceptance Scenarios**:

1. **Given** a ticket-status request with no identifiable ticket ID, **When** the request is streamed, **Then** the stream emits `intent` followed by `error` that explains a ticket ID is required, and the stream terminates without `done`.
2. **Given** a ticket-status request with no identifiable ticket ID, **When** processing occurs, **Then** no `tool_call` event is emitted.

---

### User Story 3 - Preserve Existing Behavior for Other Requests (Priority: P2)

As a product owner, I want non-ticket-status action requests and prior-stage behaviors unchanged so this slice can be released without regressions.

**Why this priority**: The slice must add focused value while maintaining previously delivered contracts.

**Independent Test**: Can be fully tested by re-running existing stage-1/stage-2 scenarios and non-ticket action_request messages to confirm unchanged validation, disconnect behavior, and placeholder handling.

**Acceptance Scenarios**:

1. **Given** an `action_request` that is not a ticket-status lookup (for example password reset), **When** streamed, **Then** existing placeholder behavior remains in place.
2. **Given** existing validation and disconnect tests from prior slices, **When** test suites run, **Then** all prior contracts still pass unchanged.

---

### Edge Cases

- What happens when a message contains multiple ticket-like IDs? The first clearly identified ticket ID is used and processed deterministically.
- How does the system handle ticket IDs with mixed case or surrounding punctuation? Ticket ID extraction normalizes case and ignores adjacent punctuation before lookup.
- What happens when the tool output contains an unsupported status or priority value? Output validation fails and returns a system `error` event because this is a contract violation.
- How does the system handle empty or whitespace-only ticket IDs after extraction? Treat as missing ticket ID and return a user-correctable `error` event.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST provide a FastMCP tool named `ticket_status_lookup` that accepts a `ticket_id` and returns status details from a mocked in-memory ticket store.
- **FR-002**: System MUST validate tool input with `TicketStatusRequest` containing `ticket_id: str` and reject empty or invalid input before tool execution.
- **FR-003**: System MUST validate tool output with `TicketStatusResponse` containing `ticket_id`, `status`, `priority`, `summary`, and `last_updated`.
- **FR-003A**: System MUST format `last_updated` as UTC ISO 8601 with `Z` suffix (for example `2026-08-25T14:30:00Z`).
- **FR-004**: System MUST support only these status values in tool output: `open`, `in_progress`, `resolved`, `closed`.
- **FR-005**: System MUST support only these priority values in tool output: `low`, `medium`, `high`, `critical`.
- **FR-006**: System MUST classify ticket-status-oriented action requests and route them to a new `check_ticket_status` node.
- **FR-007**: System MUST keep non-ticket-status `action_request` messages on the current placeholder-response path for this slice.
- **FR-008**: System MUST extract a ticket ID from the user message before invoking the ticket status tool, and MUST recognize only IDs matching `TKT-<digits>` with a case-insensitive `TKT-` prefix.
- **FR-009**: System MUST emit an `error` event explaining that a ticket ID is required when no ticket ID can be identified, and MUST NOT invoke the tool in that case.
- **FR-010**: System MUST treat unknown but well-formed ticket IDs as an expected business outcome by returning a `token` event with a clear not-found message, not an `error` event.
- **FR-010A**: System MUST normalize extracted ticket IDs to uppercase prefix form (`TKT-<digits>`) before lookup.
- **FR-011**: System MUST emit events for successful ticket lookup in this order: `intent` -> `tool_call` -> `token` -> `done`.
- **FR-012**: System MUST include validated `TicketStatusResponse` data in the successful `tool_call` event payload.
- **FR-012A**: System MUST encode `TicketStatusResponse` in `tool_call` as JSON-serialized text inside the existing `data` string field.
- **FR-013**: System MUST emit a natural-language summary `token` event after a successful `tool_call` event.
- **FR-014**: System MUST preserve existing stage-1 and stage-2 behavior for validation errors, disconnect handling, and direct-response/non-ticket placeholder flows.
- **FR-015**: System MUST keep out-of-scope capabilities unimplemented in this slice: password reset tool, ticket creation tool, RAG/ChromaDB, PII redaction, prompt injection detection, long-term memory, Phoenix/Promptfoo, React frontend.

### Key Entities *(include if feature involves data)*

- **TicketStatusRequest**: User-provided tool input containing one field, `ticket_id`, used to request ticket status.
- **TicketStatusResponse**: Validated ticket-status payload containing `ticket_id`, `status`, `priority`, `summary`, and `last_updated`.
- **ToolCallEventData**: JSON-serialized string representation of `TicketStatusResponse` carried in the `data` field when `event_type` is `tool_call`.
- **MockTicketRecord**: In-memory representation of a support ticket used as the authoritative lookup source for this slice.
- **TicketStatusLookupResult**: Outcome model for lookup processing with either a validated ticket status payload or a not-found outcome message.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of valid ticket-status requests with existing ticket IDs return event sequence `intent` -> `tool_call` -> `token` -> `done` in contract tests.
- **SC-002**: 100% of ticket-status requests without an identifiable ticket ID return `intent` then `error`, with no `tool_call`, in contract tests.
- **SC-003**: 100% of requests with well-formed but unknown ticket IDs return a not-found `token` response and `done`, with no `error`, in contract tests.
- **SC-004**: 100% of existing stage-1 and stage-2 contract tests continue to pass with no behavior changes.
- **SC-005**: At least 95% of successful ticket-status test requests complete their full stream sequence in under 2 seconds in local verification runs.

## Assumptions

- Ticket IDs in this slice are recognized only as `TKT-<digits>` (case-insensitive input prefix, normalized before lookup).
- The mocked in-memory ticket store includes a small fixed sample set adequate for deterministic testing.
- `last_updated` is treated as a string in this slice and does not require date parsing or timezone normalization.
- Expected user-correctable outcomes (such as unknown ticket IDs) are communicated through normal token responses rather than system error events.
- This slice does not add any new authentication, authorization, or data persistence requirements beyond existing project behavior.
