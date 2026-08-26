# HTTP Contract: PII Redaction and Prompt Injection Guard

## Endpoint: POST /chat/stream

### Request body
- Contract remains `ChatRequest`.
- Required fields and validation behavior remain unchanged.

### Stream envelope (unchanged)

```json
{
  "event_type": "intent | token | tool_call | error | done",
  "data": "string"
}
```

## Pre-classification guardrail contract
- Every incoming message is processed by safety checks before intent classification.
- Safety checks run in this order:
  1. Prompt-injection detection on normalized text (case-insensitive, whitespace-normalized matching).
  2. PII redaction for email and phone placeholders on non-blocked messages.

## Blocked prompt-injection contract
- If injection is detected:
  - emit `error` as first stream event
  - do not emit `intent`, `token`, `tool_call`, or `done`
  - do not execute classification, retrieval, tool calls, or LLM generation
- `error` event payload requirements:
  - `data` is a JSON-encoded string
  - contains `error_code` set to `ERR-PROMPT-INJECTION-BLOCKED`
  - contains `message` set to `Request blocked for safety.`

Example blocked event payload:

```json
{
  "event_type": "error",
  "data": "{\"error_code\":\"ERR-PROMPT-INJECTION-BLOCKED\",\"message\":\"Request blocked for safety.\"}"
}
```

## Non-blocked PII redaction contract
- If no injection is detected:
  - emails are replaced with `[REDACTED_EMAIL]`
  - phone numbers are replaced with `[REDACTED_PHONE]`
  - redacted message proceeds through normal existing flow
- Existing stream behavior remains unchanged for legitimate requests:
  - normal path: `intent` then `token` content then `done`
  - generation failure path: `intent` then `error`, no `done`

Example non-blocked redaction behavior:

Request message:

```text
Contact me at alice@example.com or +1 (555) 123-4567
```

Downstream processed message:

```text
Contact me at [REDACTED_EMAIL] or [REDACTED_PHONE]
```

Expected stream sequence:

```json
{"event_type":"intent","data":"direct_response"}
{"event_type":"token","data":"..."}
{"event_type":"done","data":""}
```

## Regression constraints
- Stage 1-4 validation behavior and existing error-code contracts remain unchanged.
- Disconnect handling remains unchanged.
- Intent classification, RAG retrieval, and ticket/tool logic remain unchanged except for earlier guardrail insertion.

## Explicit out of scope
- password reset tool
- ticket creation tool
- long-term memory
- Arize Phoenix instrumentation
- Promptfoo evaluation
- React frontend
- LLM-based injection classifier
