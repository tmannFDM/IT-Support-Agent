# Data Model: FastMCP Ticket Status Slice

## Entity: TicketStatusRequest
- Purpose: Validated input contract for `ticket_status_lookup` tool calls.
- Fields:
  - ticket_id: str
- Validation rules:
  - Required, non-empty after trimming.
  - Must match `TKT-<digits>` pattern (case-insensitive input accepted before normalization).

## Entity: TicketStatusResponse
- Purpose: Validated output contract from `ticket_status_lookup` tool and serialized `tool_call` stream payload source.
- Fields:
  - ticket_id: str
  - status: Literal[open, in_progress, resolved, closed]
  - priority: Literal[low, medium, high, critical]
  - summary: str
  - last_updated: str
- Validation rules:
  - `ticket_id` normalized to uppercase `TKT-<digits>` form.
  - `status` constrained to declared enum values.
  - `priority` constrained to declared enum values.
  - `summary` required non-empty text.
  - `last_updated` must be UTC ISO 8601 with `Z` suffix.

## Entity: MockTicketRecord
- Purpose: In-memory authoritative ticket state for this slice.
- Storage shape:
  - Key: normalized ticket ID (`TKT-####`)
  - Value: object containing `status`, `priority`, `summary`, `last_updated`
- Validation rules:
  - Keys must satisfy ticket ID pattern.
  - Values must satisfy `TicketStatusResponse` domain constraints after re-attaching key as `ticket_id`.

## Entity: TicketStatusLookupResult
- Purpose: Internal node/tool result model to distinguish successful lookup from expected not-found and missing-ID outcomes.
- Variants:
  - Success: contains validated `TicketStatusResponse`
  - NotFound: contains normalized `ticket_id` and user-facing not-found message
  - MissingId: contains user-facing error reason; tool must not be invoked

## Entity: AgentState (Extension)
- Purpose: LangGraph state used through classify and ticket-status nodes.
- Existing fields reused:
  - user_id, session_id, message, intent, response, error
- New slice-specific optional fields:
  - ticket_id: str
  - tool_name: str
  - tool_payload_json: str
- Validation rules:
  - `ticket_id` populated only when extraction succeeds.
  - `tool_payload_json` populated only for successful ticket-status lookups and must serialize validated `TicketStatusResponse`.

## Entity: ChatStreamEvent (Existing Envelope, Extended Use)
- Purpose: Outbound SSE contract for `/chat/stream`.
- Fields:
  - event_type: Literal[token, tool_call, error, done, intent]
  - data: str
- State transitions for ticket-status path:
  - Successful lookup:
    1. intent
    2. tool_call (`data` contains JSON-serialized `TicketStatusResponse`)
    3. token (natural-language summary)
    4. done
  - Missing ticket ID:
    1. intent
    2. error
    3. terminate without done
  - Unknown ticket ID:
    1. intent
    2. token (not-found message)
    3. done

## Regression Contract Entities (Unchanged)
- ValidationErrorResponse:
  - HTTP 422, `error_code=ERR-VALIDATION-MISSING-FIELD`, existing details shape preserved.
- DisconnectTermination:
  - Immediate generation stop on disconnect, no retry, no post-disconnect events.
