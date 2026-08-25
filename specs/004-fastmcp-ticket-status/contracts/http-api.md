# HTTP Contract: FastMCP Ticket Status Slice

## Endpoint: POST /chat/stream

### Request body
- Contract: `ChatRequest` (unchanged)
- Required fields: `user_id`, `session_id`, `message`
- Existing trim/validation and 422 error shape remain unchanged.

### Stream event envelope (unchanged)

```json
{
  "event_type": "intent | token | tool_call | error | done",
  "data": "string"
}
```

### Ticket-status routing rule
- Only action-request messages that ask for ticket status and contain a recognizable `TKT-<digits>` candidate are processed by `check_ticket_status` flow.
- Non-ticket action_request messages keep existing placeholder behavior.

### tool_call payload contract for ticket-status success
- `event_type`: `tool_call`
- `data`: JSON-serialized `TicketStatusResponse` string (not an object at envelope level)

Serialized JSON schema shape:

```json
{
  "ticket_id": "TKT-1001",
  "status": "open | in_progress | resolved | closed",
  "priority": "low | medium | high | critical",
  "summary": "string",
  "last_updated": "YYYY-MM-DDTHH:MM:SSZ"
}
```

### Required stream sequences

- ticket-status success (existing ticket):
  1. `intent` event (contains classified intent)
  2. `tool_call` event (`data` = JSON-serialized validated `TicketStatusResponse`)
  3. `token` event with natural-language ticket summary
  4. `done` event

- ticket-status missing ID:
  1. `intent` event
  2. `error` event explaining ticket ID is required
  3. stream terminates without `done`

- ticket-status unknown but well-formed ID:
  1. `intent` event
  2. `token` event with clear not-found message
  3. `done` event

- non-ticket action_request:
  1. `intent` event
  2. `token` event(s) containing existing unsupported placeholder
  3. `done` event

### Ticket ID format and normalization
- Extraction pattern: `TKT-<digits>` (case-insensitive input matching).
- Normalization: resolved ticket ID is transformed to uppercase `TKT-<digits>` before lookup and payload emission.

### Validation regression requirements (unchanged)
- Missing/empty/whitespace-only required request fields:
  - Status: 422
  - `error_code`: `ERR-VALIDATION-MISSING-FIELD`
  - Message and details shape preserved

### Disconnect regression requirements (unchanged)
- Mid-stream disconnect:
  - generation stops immediately
  - no retry
  - no further events

## Endpoint: GET /health
- Contract unchanged
- Status 200 with existing fields

## Explicitly out of scope for this slice
- Password-reset tool
- Ticket-creation tool
- RAG/ChromaDB retrieval
- PII redaction
- Prompt injection detection
- Long-term memory
- Phoenix instrumentation
- Promptfoo evaluation
- React frontend
