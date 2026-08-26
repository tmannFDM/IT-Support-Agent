# Data Model: Ticket Creation Tool Slice

## Entity: TicketCreateRequest
- Purpose: Validated input contract for `create_ticket` tool.
- Fields:
  - category: Literal[`VPN`, `Password`, `Hardware`, `Software`, `Access`]
  - priority: Literal[`low`, `medium`, `high`, `critical`]
  - summary: str
- Validation rules:
  - category must be one of the five allowed literals.
  - priority must be one of the four allowed literals.
  - summary must be non-empty after trimming.

## Entity: TicketCreateResponse
- Purpose: Structured tool output for successful ticket creation.
- Fields:
  - ticket_id: str (`TKT-####`)
  - category: Literal[`VPN`, `Password`, `Hardware`, `Software`, `Access`]
  - priority: Literal[`low`, `medium`, `high`, `critical`]
  - status: Literal[`open`]
  - summary: str
- Validation rules:
  - ticket_id must match `^TKT-\d{4}$`.
  - ticket_id uniqueness is guaranteed by collision-scan increment logic against current store.
  - status is always `open` for this slice.

## Entity: TicketStoreEntry (shared in-memory record)
- Purpose: Canonical in-memory ticket representation shared with existing ticket-status lookup path.
- Fields:
  - ticket_id: str
  - category: str
  - priority: str
  - status: str
  - summary: str
- Validation rules:
  - ticket_id unique within the in-memory store.
  - new entries are immediately visible to status lookup reads.

## Entity: TicketCreationInferenceResult (internal agent decision)
- Purpose: Captures deterministic parsing outcome before tool call.
- Fields:
  - is_ticket_create_intent: bool
  - has_valid_ticket_id_reference: bool
  - inferred_category: Literal[`VPN`, `Password`, `Hardware`, `Software`, `Access`] | None
  - inferred_priority: Literal[`low`, `medium`, `high`, `critical`]
  - should_error_for_vague_description: bool
- Decision rules:
  - Mixed category match uses precedence: Access > VPN > Password > Hardware > Software.
  - Missing severity keywords defaults priority to `medium`.
  - Presence of valid ticket ID takes status-lookup route precedence over create route.

## State Transitions
1. action_request + valid ticket_id detected -> route to existing status-lookup node/path.
2. action_request + create intent + category inferred -> call create_ticket tool -> emit tool_call payload and token confirmation.
3. action_request + create intent + no category inferred -> return error; no ticket is written.
4. newly created ticket_id -> immediately available for subsequent status lookup.
