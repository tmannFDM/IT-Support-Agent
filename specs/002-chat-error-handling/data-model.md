# Data Model: Chat Error Handling Baseline

## Entity: ChatRequest
- Purpose: Input contract for `POST /chat/stream`.
- Fields:
  - `user_id: str` (required)
  - `session_id: str` (required)
  - `message: str` (required)
- Validation rules:
  - Trim leading/trailing whitespace before final validation.
  - Reject if missing, empty, or empty-after-trim.
- Relationships:
  - Valid request may produce stream events.
  - Invalid request maps to `ValidationErrorResponse`.

## Entity: ValidationErrorResponse
- Purpose: Stable error payload for request validation failures in this pass.
- Fields:
  - `error_code: str` (fixed value for this pass: `ERR-VALIDATION-MISSING-FIELD`)
  - `message: str` (human-readable description)
  - `details: list[ValidationErrorDetail]` (optional)
- Validation rules:
  - Used with HTTP 422 for missing/empty/whitespace-only required input errors.
  - If `details` is present, include all invalid required fields detected.

## Entity: ValidationErrorDetail
- Purpose: Field-level validation detail item.
- Fields:
  - `field: str` (invalid field name)
  - `issue: str` (reason text)
- Validation rules:
  - Must conform to object shape `{ "field": "<name>", "issue": "<reason>" }`.

## Entity: ChatStreamEvent
- Purpose: Stream event envelope for `/chat/stream`.
- Fields:
  - `event_type: Literal["token", "tool_call", "error", "done"]`
  - `data: str`
- State transitions:
  - Normal path: `token` (1..n) then terminal `done`.
  - Disconnect path: stream stops immediately; no retry; no further events.

## Entity: HealthStatus
- Purpose: Response payload for `GET /health`.
- Fields:
  - `status: str`
  - `version: str`
- Validation rules:
  - Both are non-empty strings for contract checks.
