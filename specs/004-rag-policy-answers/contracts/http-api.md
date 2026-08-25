# HTTP Contract: RAG Policy Answers Slice

## Endpoint: POST /chat/stream

### Request body
- Contract remains `ChatRequest`.
- Required fields remain unchanged (`user_id`, `session_id`, `message`).
- Existing validation and 422 error shape remain unchanged.

### Stream envelope (unchanged)

```json
{
  "event_type": "intent | token | tool_call | error | done",
  "data": "string"
}
```

## Policy-question routing contract
- `policy_question` intent MUST route to `answer_policy_question` node.
- Placeholder response path for `policy_question` is replaced by retrieval-grounded answer path.

## Retrieval and fallback contract
- Retrieval query uses top 3 chunks.
- Only chunks with relevance score >= 0.35 are considered usable context.
- If no chunks meet threshold:
  - Do not call LLM.
  - Return exact fallback text: `I don't have information on that policy.`

## Generation prompt behavior contract
- LLM generation prompt must instruct:
  - answer only from provided retrieved context
  - explicitly avoid adding unsupported information
  - indicate unavailable info when context does not answer

## Required stream sequences for policy_question

### A) On-topic grounded answer
1. `intent` event (`policy_question`)
2. `token` event(s) containing grounded answer text
3. answer includes source filename citation(s), for example `Source: vpn_policy.md`
4. `done` event

Example SSE payload sequence:

```json
{"event_type":"intent","data":"policy_question"}
{"event_type":"token","data":"VPN access requires manager approval.\n\nSources: vpn_policy.md"}
{"event_type":"done","data":""}
```

### B) Off-topic / no relevant context
1. `intent` event (`policy_question`)
2. `token` event with exact fallback text
3. `done` event

Example fallback token:

```json
{"event_type":"token","data":"I don't have information on that policy."}
```

### C) Generation failure after retrieval
1. `intent` event (`policy_question`)
2. `error` event
3. stream terminates without `done`

## Regression requirements (unchanged)
- stage-1 validation error behavior unchanged
- stage-1 disconnect behavior unchanged
- stage-2 direct_response behavior unchanged
- stage-3 ticket_status action_request behavior unchanged

## Endpoint: GET /health
- Unchanged

## Explicit out of scope
- Any src/tools additions
- src/security
- src/observability
- password reset / ticket creation tools
- PII redaction
- prompt injection detection
- long-term memory
- Arize Phoenix
- Promptfoo
- React frontend
