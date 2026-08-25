# HTTP Contract: Chat Error Handling Baseline

## Endpoint: `POST /chat/stream`

### Request
- Method: `POST`
- Content-Type: `application/json`
- Body contract: `ChatRequest`

```json
{
  "user_id": "string",
  "session_id": "string",
  "message": "string"
}
```

### Validation behavior
For required fields `user_id`, `session_id`, and `message`:
- Trim leading/trailing whitespace before final validation.
- Missing, empty, or empty-after-trim values are invalid.

### Validation failure response
- Status: `422 Unprocessable Entity`
- Content-Type: `application/json`
- Required payload keys:
  - `error_code` (value: `ERR-VALIDATION-MISSING-FIELD`)
  - `message` (human-readable)
- Optional payload key:
  - `details`: list of all invalid required fields in request

`details` item schema:

```json
{
  "field": "<name>",
  "issue": "<reason>"
}
```

Example failure response:

```json
{
  "error_code": "ERR-VALIDATION-MISSING-FIELD",
  "message": "Validation failed for required fields.",
  "details": [
    { "field": "user_id", "issue": "Field required or empty after trim" },
    { "field": "message", "issue": "Field required or empty after trim" }
  ]
}
```

### Success response
- Status: `200 OK`
- Content-Type: `text/event-stream`
- Event payload contract: `ChatStreamEvent`

```json
{
  "event_type": "token | tool_call | error | done",
  "data": "string"
}
```

For this pass:
- Implemented success events are `token` and terminal `done`.
- If client disconnects mid-stream, generation stops immediately, no retry is attempted, and no further events are sent.

## Endpoint: `GET /health`

### Success response
- Status: `200 OK`
- Content-Type: `application/json`

```json
{
  "status": "ok",
  "version": "0.1.0"
}
```

## Explicit Out-of-Scope Error Codes
This pass does not define additional codes for:
- PII redaction
- Prompt injection handling
- Tool failures
- Other deferred capability domains
