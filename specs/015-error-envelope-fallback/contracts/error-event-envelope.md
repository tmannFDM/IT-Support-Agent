# Contract: Error Event Envelope

## Scope

This document clarifies the payload carried by the existing `error` stream event. It does not add an endpoint, event type, or schema.

## Stream Event

```text
data: {"event_type":"error","data":"{\"error_code\":\"ERR-LLM-GENERATION-FAILED\",\"message\":\"LLM service unavailable\"}"}
```

The outer event remains the existing stream event envelope. Its `data` value is a JSON-serialized Error Envelope.

## Error Envelope Fields

```json
{
  "error_code": "ERR-LLM-GENERATION-FAILED",
  "message": "LLM service unavailable"
}
```

| Failure source | `error_code` | Event lifecycle |
|---|---|---|
| Direct response generation | `ERR-LLM-GENERATION-FAILED` | `intent`, then `error`, no `done` |
| Policy answer generation | `ERR-POLICY-GENERATION-FAILED` | `intent`, then `error`, no `done` |

## Consumer Compatibility

Consumers must display a generic non-empty fallback message when the error event data is absent, malformed, not an object, missing `message`, or has an empty message. A valid non-empty `message` is rendered; untrusted raw payload content is not shown directly.