# HTTP Contract: Injection Pattern Expansion

## Endpoint: POST /chat/stream

### Request body
- Contract remains unchanged.

### Stream envelope
- Contract remains unchanged:

```json
{
  "event_type": "intent | token | tool_call | error | done",
  "data": "string"
}
```

## Behavioral Contract (unchanged)
- No changes to detection mechanism, guardrail routing, or blocked response shape.
- Messages matching newly added phrases follow existing blocked behavior:
  - first event is `error`
  - payload remains JSON-encoded in `data`
  - `error_code` remains `ERR-PROMPT-INJECTION-BLOCKED`
  - no `intent`, `token`, `tool_call`, or `done` events for blocked requests

## Pattern Coverage Expansion
- This pass only extends the phrase list categories:
  - instruction dismissal variants
  - persona/role override variants
  - system prompt extraction variants
  - explicit override framing variants

## Regression Expectation
- Existing non-injection and prior-stage behaviors remain unchanged.
- Existing contract tests remain valid with one added missed-phrase test.
