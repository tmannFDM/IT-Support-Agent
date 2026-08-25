# Data Model: Chat Stream Vertical Slice

## Entity: ChatRequest
- Purpose: Input contract for `POST /chat/stream`.
- Fields:
  - `user_id: str` with `min_length=1`
  - `session_id: str` with `min_length=1`
  - `message: str` with `min_length=1`, `max_length=4000`
- Validation rules:
  - Required fields must be present.
  - Empty-string values are invalid.
  - Overlength messages are invalid.
- Relationships:
  - One `ChatRequest` yields a stream of one or more `ChatStreamEvent` records.

## Entity: ChatStreamEvent
- Purpose: SSE event payload contract for stream output.
- Fields:
  - `event_type: Literal["token", "tool_call", "error", "done"]`
  - `data: str`
- Validation rules:
  - `event_type` must be one of allowed literals.
  - `data` must be a string.
- State transitions:
  - Success path: `token` (1..n) -> `done` (exactly once, terminal).
  - Error path: `error` (terminal) when stream cannot continue.

## Entity: ValidationErrorEnvelope
- Purpose: API error contract for request validation failures.
- Fields:
  - `error_code: str` (must include `ERR-VALIDATION-MISSING-FIELD` for missing/empty required-field errors)
  - `message: str`
  - `details: list[object] | null`
- Validation rules:
  - Missing/empty required-field failures map to `ERR-VALIDATION-MISSING-FIELD`.

## Entity: HealthStatus
- Purpose: Readiness payload for `GET /health`.
- Fields:
  - `status: str` (example: `ok`)
  - `version: str` (service version identifier)
- Validation rules:
  - Both fields are non-empty strings.

## Reserved Forward-Compatibility Entities
The following schemas are defined and retained for future slices, but not used in this transport-only pass:
- `ToolCallCard`
- `TicketStatusResponse`
- `PasswordResetRequest`
- `TicketCreateRequest`
