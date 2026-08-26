# HTTP Contract: Password Reset Escalation ToolCall Fix

## Endpoint: POST /chat/stream

### Request body
- Unchanged.

### Stream envelope
- Unchanged wrapper:

```json
{
  "event_type": "intent | token | tool_call | error | done",
  "data": "string"
}
```

## Escalation bug-fix contract
For escalated password-reset outcomes, content events are:
1. `tool_call` carrying JSON PasswordResetResponse payload with:
   - `employee_id`
   - `status` = `escalated`
   - `temporary_password_note`
   - `escalation_reason` in {`invalid_employee_id`, `urgency_pressure`, `vague_reason`}
2. `token` carrying human-readable escalation text only.

## Escalation sequence
- Full sequence remains:
  1. intent
  2. tool_call
  3. token
  4. done

## Clean token contract
Escalation token text must not include:
- internal field keys (for example `escalation_reason`)
- underscore-based identifier fragments
- key=value fragments

## Unchanged contracts
- Success reset path remains intent -> tool_call -> token -> done.
- Unexpected runtime failure remains intent -> error -> no done.
- Ticket-status, RAG, and stage-5 guardrail behavior remain unchanged.
