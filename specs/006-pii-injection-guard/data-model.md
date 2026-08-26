# Data Model: PII Redaction and Prompt Injection Guard

## Entity: RedactionResult
- Purpose: Captures sanitized message and detection markers before downstream processing.
- Fields:
  - original_message: str
  - redacted_message: str
  - redacted_email_count: int
  - redacted_phone_count: int
  - pii_detected: bool
- Validation rules:
  - `redacted_message` must preserve non-PII text order.
  - Every detected email must be replaced by `[REDACTED_EMAIL]`.
  - Every detected phone number must be replaced by `[REDACTED_PHONE]`.

## Entity: InjectionDetectionResult
- Purpose: Indicates whether a message should be blocked before classification.
- Fields:
  - normalized_message: str
  - injection_detected: bool
  - matched_pattern_count: int
- Validation rules:
  - Matching is case-insensitive.
  - Matching occurs after trim + repeated-space normalization.

## Entity: MessageSafetyCheckResult
- Purpose: Combined pre-classification guardrail outcome.
- Fields:
  - blocked: bool
  - redaction_result: RedactionResult
  - detection_result: InjectionDetectionResult
  - blocked_error_code: str | null
  - blocked_error_message: str | null
- State transitions:
  - blocked path: emit immediate error and terminate stream path
  - non-blocked path: continue with redacted_message into existing graph logic

## Entity: BlockedErrorPayload
- Purpose: Payload serialized into existing error event `data` string field.
- Fields:
  - error_code: str (fixed: `ERR-PROMPT-INJECTION-BLOCKED`)
  - message: str (fixed: `Request blocked for safety.`)
- Validation rules:
  - Serialized as JSON string value inside `ChatStreamEvent.data`.
  - Must not include matched phrase details.

## Entity: ChatStreamEvent (existing envelope)
- Purpose: Stream transport contract for `/chat/stream`.
- Fields:
  - event_type: `intent | token | tool_call | error | done`
  - data: str
- Guardrail path behavior:
  - blocked injection: first event is `error`; no `intent`, `token`, `tool_call`, or `done`
  - non-blocked: unchanged prior behavior with intent-first semantics
