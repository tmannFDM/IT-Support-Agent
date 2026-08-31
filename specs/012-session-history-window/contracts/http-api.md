# HTTP Contract: In-Session Conversation History Window

## Endpoint: POST /chat/stream

### Request body
- Existing request schema remains unchanged:
  - `user_id: string`
  - `session_id: string`
  - `message: string`

### Stream envelope
- Existing SSE event contract remains unchanged:

```json
{
  "event_type": "intent | token | tool_call | error | done",
  "data": "string"
}
```

## Session history behavior contract
1. System maintains an in-memory short-term history window keyed by `session_id`.
2. History is ephemeral and does not persist across service restarts.
3. Stored turn fields are redacted text only for both user and assistant messages.
4. History append occurs only after the request reaches completion (`done` event path).
5. Failed/interrupted responses do not create a completed history entry.
6. Max retained exchanges per session is fixed at 5; oldest entry is evicted when adding the 6th.

## Prompt construction contract
- For `direct_response` and `policy_question` LLM calls:
  - Include prior conversation turns from that same `session_id` as ordered user/assistant messages before current request context.
  - If no history exists, behavior matches current single-turn prompting.
- For tool-invoking paths (`ticket status`, `password reset`, `ticket creation`):
  - Extraction and routing remain based on current message only.
  - No history parameter is required by or passed into their extraction/routing logic in this slice.

## Session isolation contract
- Short-term history is isolated strictly by `session_id`.
- A new `session_id` always starts with empty short-term history, even with the same `user_id`.
- History from one session must never be visible in another session's prompt context.

## Compatibility contract
- No new API endpoint is introduced for short-term history.
- Long-term per-user memory behavior is unchanged.
- RAG retrieval behavior and safety guardrail semantics remain unchanged aside from reading already-redacted current message as history source.

## Acceptance-oriented contract scenarios
1. Same-session follow-up prompt includes prior turn context and supports elliptical follow-up interpretation.
2. New session with same user_id has empty short-term history in LLM payload.
3. Window eviction retains most recent five entries and drops the oldest when appending the sixth.
4. Tool-invoking request behavior remains identical with or without pre-existing session history.
