# Data Model: React Frontend Chat Experience

## Entity: ClientSessionIdentity
- Purpose: Correlate chat requests within one loaded page session.
- Fields:
  - user_id: string (UUID)
  - session_id: string (UUID)
- Validation rules:
  - Both identifiers are generated once on app mount.
  - Both are included in every `/chat/stream` POST request.

## Entity: ChatMessage
- Purpose: Renderable timeline item in conversation view.
- Fields:
  - id: string
  - role: Literal[`user`, `assistant`, `error`]
  - content: string
  - isStreaming: boolean
  - toolCard: ToolCardModel | null
- Validation rules:
  - User message is appended immediately on submit.
  - Assistant message starts as streaming placeholder and grows with token events.
  - Error message contains safe parsed message text only.

## Entity: StreamEventEnvelope
- Purpose: Parsed event from SSE-style `data:` line payload.
- Fields:
  - event_type: Literal[`intent`, `token`, `tool_call`, `error`, `done`]
  - data: string
- Validation rules:
  - Unknown event types are ignored safely.
  - `intent` is logged for debugging, not rendered as chat message.

## Entity: ToolCardModel
- Purpose: Structured UI representation for backend action results.
- Variants:
  - TicketStatusCardModel:
    - ticket_id: string
    - status: string
    - priority: string
    - category: string
    - summary: string
  - PasswordResetCardModel:
    - status: string
    - temporary_password_note: string
    - escalation_reason: string | null
  - TicketCreateCardModel:
    - ticket_id: string
    - category: string
    - priority: string
    - status: string
- Validation rules:
  - `tool_call` data is JSON-decoded and variant-matched by field shape.
  - Unmatched payload falls back to safe unknown-tool presentation.

## Entity: ChatRequestPayload
- Purpose: Request body sent to backend chat stream endpoint.
- Fields:
  - user_id: string
  - session_id: string
  - message: string
- Validation rules:
  - Empty/whitespace-only messages are blocked client-side.
  - Backend validation errors are handled gracefully via error UI path.

## State Transitions
1. User submits valid message -> append user message -> create pending assistant message -> set loading.
2. Stream parser emits token -> append token text to current assistant message.
3. Stream parser emits tool_call -> parse payload -> attach card to assistant response thread.
4. Stream parser emits error -> append error message and stop loading.
5. Stream parser emits done -> mark assistant message complete and re-enable input.
