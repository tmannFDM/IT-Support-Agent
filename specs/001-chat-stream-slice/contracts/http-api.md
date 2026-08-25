# HTTP Contract: Chat Stream Vertical Slice

## Overview
This contract defines the MVP transport API for the first backend slice.

## Endpoint: `POST /chat/stream`

### Request Body Schema
`application/json`

```json
{
  "user_id": "string (min length 1)",
  "session_id": "string (min length 1)",
  "message": "string (min length 1, max length 4000)"
}
```

Contract source: `ChatRequest` (Pydantic v2)

### Success Response
- Status: `200 OK`
- Content-Type: `text/event-stream`
- Transfer: streamed SSE frames

Each SSE frame contains JSON serialized `ChatStreamEvent`:

```json
{
  "event_type": "token | tool_call | error | done",
  "data": "string"
}
```

For this pass:
- Allowed to emit `token` and `done` for successful requests.
- `done` is terminal and must be emitted once per successful stream.

### Validation Failure Response
- Status: `422 Unprocessable Entity` (or mapped framework-equivalent validation status)
- Content-Type: `application/json`
- Must include machine-readable code:
  - `ERR-VALIDATION-MISSING-FIELD` for missing required fields and empty required values.

Example shape:

```json
{
  "error_code": "ERR-VALIDATION-MISSING-FIELD",
  "message": "Validation failed for required fields.",
  "details": [
    {
      "field": "message",
      "issue": "Field required or empty"
    }
  ]
}
```

## Endpoint: `GET /health`

### Success Response
- Status: `200 OK`
- Content-Type: `application/json`

```json
{
  "status": "ok",
  "version": "0.1.0"
}
```

## Out of Scope Contract Notes
- No intent classification contract.
- No RAG retrieval contract.
- No tool-call execution contract.
- No LangGraph state contract.
- No long-term memory contract.
