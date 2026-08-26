# HTTP Contract: Ticket Creation Tool Slice

## Endpoint: POST /chat/stream

### Request body
- Existing request envelope remains unchanged.

### Stream envelope
- Existing wrapper remains unchanged:

```json
{
  "event_type": "intent | token | tool_call | error | done",
  "data": "string"
}
```

## Ticket-creation success contract
For a clear, categorizable ticket-creation action request without a status-lookup precedence hit:
1. Emit `intent` with `action_request`.
2. Emit `tool_call` containing a serialized `TicketCreateResponse` JSON payload.
3. Emit `token` confirmation that includes the newly generated `ticket_id`.
4. Emit `done`.

`tool_call` payload fields:
- `ticket_id` (`TKT-####`)
- `category` in {`VPN`, `Password`, `Hardware`, `Software`, `Access`}
- `priority` in {`low`, `medium`, `high`, `critical`}
- `status` = `open`
- `summary` (user issue summary)

## Uncategorizable create-request contract
For create-intent action requests with no category keyword match:
1. Emit `intent` with `action_request`.
2. Emit `error` requesting more issue detail.
3. Do not emit `tool_call` for ticket creation.
4. Do not create a new ticket in the shared store.

## Mixed-intent precedence contract
If a valid ticket ID pattern is present in the same message as ticket-creation cues:
- Status-lookup route takes precedence over create-ticket route.
- Existing ticket-status lookup stream behavior remains authoritative.

## Shared-store compatibility contract
After successful ticket creation:
- the returned `ticket_id` must be immediately queryable through existing ticket-status lookup behavior,
- without changing the lookup tool's internal logic.

## Unchanged contracts
- Password reset behavior and payload contracts remain unchanged.
- RAG policy-answer behavior remains unchanged.
- Prompt-injection and PII guardrail contracts remain unchanged.
- Generic non-ticket action-request fallback remains unchanged unless routed into this new slice.
