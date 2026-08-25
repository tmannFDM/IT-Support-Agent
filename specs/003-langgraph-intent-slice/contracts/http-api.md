# HTTP Contract: LangGraph Intent Slice

## Endpoint: POST /chat/stream

### Request body
- Contract: ChatRequest (unchanged from stage-1)
- Required fields: user_id, session_id, message
- Existing trim/validation and 422 error shape remain unchanged.

### Stream event contract
ChatStreamEvent extends event_type to include intent.

```json
{
  "event_type": "intent | token | tool_call | error | done",
  "data": "string"
}
```

### Intent classification behavior
- classify_intent MUST assign one of:
  - policy_question
  - action_request
  - direct_response
  - escalation
  - blocked

### Required stream sequences
- direct_response success:
  1. intent event (contains classified intent)
  2. token event(s) for generated answer
  3. done event
- non-direct intents (policy_question/action_request/escalation/blocked):
  1. intent event
  2. token event(s) containing exact placeholder text:
     This type of request isn't supported yet.
  3. done event
- direct_response LLM failure:
  1. intent event
  2. error event
  3. stream terminates without done

### Validation regression requirements
- Missing/empty/whitespace-only required fields:
  - Status: 422
  - error_code: ERR-VALIDATION-MISSING-FIELD
  - message: human-readable
  - details shape preserved

### Disconnect regression requirements
- Mid-stream disconnect:
  - generation stops immediately
  - no retry
  - no further events

## Endpoint: GET /health
- Contract unchanged from stage-1
- Status 200 with status and version fields

## Explicitly out of scope for this slice
- RAG/ChromaDB retrieval
- FastMCP tools
- PII redaction
- Prompt injection detection
- Long-term memory
- Arize Phoenix instrumentation
- Promptfoo evaluation
- React frontend
