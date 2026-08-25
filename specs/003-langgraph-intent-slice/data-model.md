# Data Model: LangGraph Intent Slice

## Entity: AgentState
- Purpose: Stateful object flowing through LangGraph nodes.
- Minimum fields:
  - user_id: str
  - session_id: str
  - message: str
  - intent: IntentLabel
  - response: str
- Validation rules:
  - user_id/session_id/message inherit existing request validation constraints.
  - intent must be one of supported intent labels.

## Entity: IntentLabel
- Purpose: Routing label for classify_intent node.
- Allowed values:
  - policy_question
  - action_request
  - direct_response
  - escalation
  - blocked
- Validation rules:
  - Exactly one label is assigned per message.

## Entity: ChatStreamEvent
- Purpose: Stream payload contract for /chat/stream.
- Fields:
  - event_type: Literal[token, tool_call, error, done, intent]
  - data: str
- State transitions:
  - Success paths (direct_response success and non-direct placeholder):
    intent -> token (1..n) -> done (exactly once)
  - direct_response generation failure path:
    intent -> error -> terminate (no done)

## Entity: PlaceholderResponse
- Purpose: Deterministic fallback output for non-direct intents.
- Value:
  - This type of request isn't supported yet.

## Entity: ValidationErrorResponse (Regression Contract)
- Purpose: Preserved stage-1 error contract for input validation failures.
- Required behavior:
  - HTTP 422
  - error_code: ERR-VALIDATION-MISSING-FIELD
  - message: human-readable
  - details (optional): complete invalid-field set with field/issue entries

## Entity: DisconnectTermination
- Purpose: Preserved stage-1 cancellation behavior.
- Required behavior:
  - On disconnect detection, stop generation immediately.
  - No retry and no post-disconnect event emission.
