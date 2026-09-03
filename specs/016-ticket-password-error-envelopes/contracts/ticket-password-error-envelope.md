# Contract: Ticket and Password Error Envelopes

## Scope

This contract documents the inner JSON payload carried by the existing stream `error` event for three ticket/password failure paths. It adds no endpoint, schema, or event type.

## Envelope

```json
{
  "error_code": "ERR-TICKET-CREATE-FAILED",
  "message": "Ticket service unavailable"
}
```

## Error Categories

| Condition | Error code | Event sequence |
|---|---|---|
| Ticket category is absent | `ERR-TICKET-CATEGORY-REQUIRED` | `intent`, `error`; no tool call or done |
| Ticket creation tool fails | `ERR-TICKET-CREATE-FAILED` | `intent`, `error`; no tool call or done |
| Password reset tool fails | `ERR-PASSWORD-RESET-FAILED` | `intent`, `error`; no tool call or done |

All paths use `action_request` for the intent event. The `message` must be non-empty. Silent exceptions are represented as `{ExceptionType} (no message)`.

## Compatibility

Successful ticket creation and successful or escalated password reset continue to produce their existing tool-call, token, and done events.