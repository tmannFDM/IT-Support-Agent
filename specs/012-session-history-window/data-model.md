# Data Model: In-Session Conversation History Window

## Entity: SessionHistoryStore
- Purpose: Ephemeral in-memory container for short-term conversation context.
- Key:
  - session_id: str
- Value:
  - ordered list/window of `SessionExchange` entries (max length 5).
- Validation rules:
  - Store is process-local and non-persistent.
  - Unknown/new `session_id` resolves to empty history.
  - Entries never cross session boundaries.

## Entity: SessionExchange
- Purpose: One completed conversational turn used as prior context.
- Fields:
  - user_message_redacted: str
  - assistant_response_redacted: str
  - appended_after_done: bool (conceptual invariant; true for stored entries)
- Validation rules:
  - User text is sourced from already-redacted `state["message"]`.
  - Assistant text is stored from finalized response text only.
  - Partial/failed/incomplete responses are not stored.

## Entity: SlidingWindowPolicy
- Purpose: Enforce bounded memory per session.
- Fields:
  - max_exchanges: int (fixed to 5 for this slice)
  - eviction_strategy: Literal[`drop_oldest_first`]
- Validation rules:
  - Length is always `<= max_exchanges`.
  - On append when full, exactly one oldest entry is evicted.

## Prompt-Context Projection
- Purpose: Transform `SessionExchange[]` into prior-turn prompt messages.
- Mapping:
  - each exchange maps to two ordered messages: user role then assistant role.
  - current request user message remains last user message in the final prompt sequence.
- Applicability rules:
  - Applied only in direct-response and policy-question LLM calls.
  - Not applied to ticket/password/ticket-creation extraction or routing paths.

## State/Flow Invariants
1. Guardrail redaction completes before LLM and before history append source user text is read.
2. Session history append occurs only after response completion for the request.
3. New session_id starts with empty window even when user_id matches another active session.
4. Long-term `user_id` memory and short-term `session_id` history remain logically and physically separate.
